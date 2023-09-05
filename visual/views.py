from pprint import pprint
from datetime import timedelta
from urllib.parse import urlparse

from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse
from django.urls import reverse
from django.utils import formats

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Sottocampo, Campo, Orario, Pezzo, CampoSottocampo, Prodotto, ContentType, Societa
from .forms import CampoForm, SottocampoForm, Sottocampo_Orario, Sottocampo_Pezzo, CustomUserCreationForm, CustomUserAuthenticationForm

# UTILITY
import random, string
def genera_codici(mappa_codici, lunghezza=8):  # da cambiare in 256 per maggior sicurezza
    codice_univoco = False
    codice = None

    while not codice_univoco:
        codice = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=lunghezza))
        codice_univoco = codice not in mappa_codici.values()

    return codice

# VIEW

class LoginUserView(LoginView):
    form_class = CustomUserAuthenticationForm
    template_name = "utenti/login.html"

# LogoutView

class RegisterUserView(View):
    form_class = CustomUserCreationForm

    def get(self, request):
        form = self.form_class()
        return render(request, "utenti/register.html", {"form": form})
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            return redirect("login")

        return self.get(request)
        # return render(request, "utenti/register.html", {"form": form})

class PermissionDeniedView(View):
    template_name = "utenti/403.html"  # Personalizza il nome del template

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, status=403)
    

class HomePageView(View):
    def get(self, request):
        return render(request, "home.html", {})
    
class NuovaSocietaView(View, LoginRequiredMixin):
    def get(self, request):
        # if not request.user.groups.filter(name="CrudSocieta").exists():
        #     return PermissionDeniedView.as_view()(self.request)
        
        return render(request, "nuova-societa.html", {})
    
    def post(self, request):
        if request.user.societa is None:
            if request.POST["nome"]:
                societa = Societa(nome=request.POST["nome"])
                societa.save()
                
                request.user.societa = societa
                request.user.save()

                return render(request, "nuova-societa.html", {"response": "società creata con successo"})

class ProdottiView(LoginRequiredMixin, View):

    def get(self, request):        
        societa = request.user.societa

        if (societa is None):
            return redirect("nuova-societa")

        codici_obj = {}
        context = {
            "prodotti": []
        }
        
        for prodotto in societa.prodotti.all():
            codice = genera_codici(codici_obj)

            codici_obj[codice] = {"pk": prodotto.pk, "tipo": "Prodotto"}
            context["prodotti"].append({
                "codice": codice,
                "obj": prodotto
            })

        request.session["codici_obj"] = codici_obj  # Salvo il dict nella session dell'utente
        # pprint(request.session["codici_obj"])

        return render(request, "prodotti.html", context)


class ProdottoView(View, LoginRequiredMixin):  # visualize.html
   def get(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        
        societa = request.user.societa

        if societa is None:
            return redirect("nuova-societa")
        
        prodotto = societa.prodotti.filter(nome_slug=slug)
        
        if not prodotto.exists():
            return HttpResponseNotFound("Il prodotto non esiste")
        
        if prodotto.count() != 1:
            return HttpResponse("Conflitto, trovati due prodotti con il seguente url! Contattare l'amministratore")
        
        prodotto = prodotto.first()

        codici_obj = {}  # generazione dei codici {codice -> {pk, tipo}}
        context = {
            "slug": slug,
            "Prodotto": prodotto,
            "Sottocampi": {"societa": [], "prodotto": []}, "Campi": [],

            "form_crea_campo": CampoForm(),
            "form_crea_sottocampo_pezzo": Sottocampo_Pezzo(),
            "form_crea_sottocampo_orario": Sottocampo_Orario()
        }

        # Sottocampi della società
        for sottocampo in societa.sottocampi.all():
            codice = genera_codici(codici_obj)

            codici_obj[codice] = {"pk": sottocampo.pk, "tipo": "Sottocampo"}
            context["Sottocampi"]["societa"].append({
                "codice": codice,
                "obj": sottocampo
            })

        # Sottocampi del prodotto
        print(prodotto.sottocampi.all())
        print(prodotto.nome, prodotto.societa)
        for sottocampo in prodotto.sottocampi.all():
            codice = genera_codici(codici_obj)

            codici_obj[codice] = {"pk": sottocampo.pk, "tipo": "Sottocampo"}
            context["Sottocampi"]["prodotto"].append({
                "codice": codice,
                "obj": sottocampo
            })

        # Campi del prodotto
        for campo in prodotto.campi.all():
            codice = genera_codici(codici_obj)

            codici_obj[codice] = {"pk": campo.pk, "tipo": "Campo"}
            context["Campi"].append({
                "codice": codice,
                "obj": campo,
                "sottocampi": [  # restituisce l'oggetto e il suo codice di riferimento
                    {
                        "codice": next((codice for codice, item in codici_obj.items() if item["tipo"] == "Sottocampo" and item["pk"] == sottocampo.pk), "Errore"),
                        "obj": sottocampo,
                        "quantita": CampoSottocampo.objects.get(sottocampo=sottocampo, campo=campo).quantita
                    } for sottocampo in campo.sottocampi.all()
                ]
            })

        request.session["codici_obj"] = codici_obj  # Salvo il dict nella session dell'utente

        return render(request, "visualize.html", context)

class NuovoCampoView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        prodotto = Prodotto.objects.filter(nome_slug=slug)
        
        if not prodotto.exists():
            return HttpResponseNotFound("Il prodotto non esiste")
        
        prodotto = prodotto.first()
        
        form = CampoForm()
        context = {"slug": slug, "form": form}
        return render(request, "nuovo-campo.html", context)
    
    def post(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        prodotto = Prodotto.objects.filter(nome_slug=slug)
        
        if not prodotto.exists():
            return HttpResponseNotFound("Il prodotto non esiste")
        
        prodotto = prodotto.first()
        
        form = CampoForm(request.POST)

        if form.is_valid():
            campo = form.save(commit=False)
            campo.prodotto = prodotto
            campo.save()

            print(reverse("visualize", kwargs={"slug": slug}))
            return redirect(reverse("visualize", kwargs={"slug": slug}))

        context = {"slug": slug, "form": form}
        return render(request, "nuovo-campo.html", context)
    
class NuovoSottocampoView(View, LoginRequiredMixin):
    def get(self, request):
        # pprint(request.GET)

        self.tipo = request.GET.get("tipo")
        context = {}

        if (self.tipo == "orario"):
            context['form'] = Sottocampo_Orario()
        else:
            context['form'] = Sottocampo_Pezzo()

        return render(request, "nuovo-sottocampo.html", context)

    def post(self, request):
        self.tipo = request.GET.get("tipo")

        # Creo nuovo sottocampo e sottocampo primario
        # pprint(request.POST)
        form = Sottocampo_Pezzo(request.POST)
        if self.tipo == "orario":
            form = Sottocampo_Orario(request.POST)

        if form.is_valid():
            sottocampo = Sottocampo(nome=request.POST["nome"], ruolo=request.POST["ruolo"])
            sottocampo.save()

            content_type, content_id = None, 0

            # Creo le istanze dei sottocampi primari e setto il ContentType (per la relazione)
            if self.tipo == "orario":
                orario = Orario(tariffa=float(request.POST["tariffa"]),
                                ore=timedelta(hours=int(request.POST["ore"])),
                                sottocampo=sottocampo)
                orario.save()
                content_type, content_id = ContentType.objects.get_for_model(orario), orario.id
            else:
                pezzo = Pezzo(costo=float(request.POST["costo"]),
                            numero=int(request.POST["numero"]),
                            sottocampo=sottocampo)
                pezzo.save()
                content_type, content_id = ContentType.objects.get_for_model(pezzo), pezzo.id

            # sottocampo = Sottocampo(
            #     nome = form.cleaned_data["nome"],
            #     ruolo = form.cleaned_data["ruolo"],

            #     content_type = content_type,
            #     content_id = content_id
            # )

            return redirect(reverse("prodotti"))
        
        return self.get(request)

## REST API

# Api del Porodotto
class ProdottiApi(APIView):
    permission_classes = [IsAuthenticated]  # hanno una società collegata a loro

    def post(self, request, format=None):
        tipo = request.data.get('tipo')

        if tipo == "CREATE":
            return self.create(request)
        elif tipo == "UPDATE":
            return self.update(request)
        elif tipo == "DELETE":
            return self.delete(request)
        
        return Response({'success': False, 'message': 'Tipo non supportato'})
        
    def create(self, request):
        societa = request.user.societa

        dati = request.data.get("dati")
        modalita = dati.get("modalita")

        # modalita == "nuovo"
        prod = Prodotto(nome=dati.get("nome"), societa=societa)  # nome e società
        prod.save()

        if modalita == "from":
            codice = dati.get("codice")
            if request.session["codici_obj"][codice]["tipo"] == "Prodotto":
                prod += Prodotto.objects.get(pk=request.session["codici_obj"][codice]["pk"])  # aggiungo i campi
                prod.save()
        elif modalita != "nuovo":
            return Response({'success': False, 'message': 'La modalità non esiste'})
        
        # Lo registro nella session
        codice_prod = genera_codici(request.session["codici_obj"])
        codici_obj = request.session["codici_obj"]
        codici_obj[codice_prod] = {"pk": prod.pk, "tipo": "Prodotto"}
        request.session["codici_obj"] = codici_obj

        # Salvo il prodotto
        prod.save()

        return Response({'success': True, 'message': 'Prodotto creato correttamente',
                         'dati': [
                            prod.nome,
                            prod.totale()["pezzo"],
                            prod.totale()["ora"],
                            prod.totale()["pezzo"] + prod.totale()["ora"],
                            formats.date_format(prod.data_creazione, "d F Y H:i"),
                            formats.date_format(prod.data_ultima_modifica, "d F Y H:i"),

                            codice_prod,
                            reverse("visualize", kwargs={"slug": prod.nome_slug})
                         ]})

    def update(self, request):
        dati = request.data.get("dati")
        azione = dati.get("azione")

        # Rinomina del prodotto
        if azione == "rinomina":
            prod_code = dati.get("prodotto")
            # print("codice prodotto:", prod_code)
            nome = dati.get("nome")

            pk, tipo = request.session["codici_obj"][prod_code]["pk"], request.session["codici_obj"][prod_code]["tipo"]

            if tipo != "Prodotto":
                return Response({'success': False, 'message': 'Il codice non corrisonde ad un prodotto'})
            
            prod = Prodotto.objects.get(pk=pk)
            prod.nome = nome
            prod.save()

            return Response({'success': True, 'message': 'Nome aggiornato correttamente', 'url': reverse("visualize", kwargs={"slug": prod.nome_slug})})

    def delete(self, request):
        dati = request.data.get("dati")
        for codice in dati.get("codici"):
            pk, tipo = request.session["codici_obj"][codice]["pk"], request.session["codici_obj"][codice]["tipo"]

            if tipo != "Prodotto":
                    return Response({'success': False, 'message': 'Il codice non corrisonde ad un prodotto'})
            
            Prodotto.objects.get(pk=pk).delete()

        return Response({'success': True, 'message': 'Eliminazione di tutti i prodotti avvenuta'})

# Api Sottocampi dei Campi
class CampoSottocampoApi(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        tipo = request.data.get('tipo')

        self.slug = urlparse(request.META.get("HTTP_REFERER")).path.split("/")[-2]
        self.societa = request.user.societa

        self.prodotto = self.societa.prodotti.filter(nome_slug=self.slug)
        
        if not self.prodotto.exists():
            return HttpResponseNotFound("Il prodotto non esiste")
        
        self.prodotto = self.prodotto.first()
        
        if tipo == "CREATE":
            return self.create(request)
        if tipo == 'UPDATE':
            return self.update(request)
        elif tipo == "DELETE":
            return self.delete(request)
        
        return Response({'success': False, 'message': 'Tipo non supportato'})
    
    def create(self, request):
        dati = request.data.get("dati")

        if dati.get("tipo") == "campo":
            form = CampoForm(dati.get("form"))

            if form.is_valid():
                campo = form.save(commit=False)
                campo.prodotto = self.prodotto

                campo.save()

                codice = genera_codici(request.session["codici_obj"])
                codici_obj = request.session["codici_obj"]
                codici_obj[codice] = {"pk": campo.pk, "tipo": "Campo"}
                request.session["codici_obj"] = codici_obj

                return Response({"success": True, "message": "campo creato con successo",
                                 "dati": {
                                     "nome": campo.nome,
                                     "codice": codice
                                 }})

            return Response({"success": False, "message": "dati non validi"})

        elif dati.get("tipo") == "sottocampo":
            tipologia = dati.get("tipologia")
            target = dati.get("target")

            if tipologia == "pezzo":
                form = Sottocampo_Pezzo(dati.get("form"))
            elif tipologia == "orario":
                form = Sottocampo_Orario(dati.get("form"))
            else:
                return Response({"success": False, "message": "tipologia non supportata"})
            
            if target != "societa" and target != "prodotto":
                return Response({"success": False, "message": "target incorretto"})

            if form.is_valid():
                dati = dati.get("form")

                sottocampo = Sottocampo.objects.create(nome = dati.get("nome"))
                # sottocampo.save()

                content_type, content_id = None, 0

                if tipologia == "pezzo":
                    pezzo = Pezzo(costo=float(dati.get("costo")),
                                  numero=int(dati.get("numero")))
                    pezzo.save()
                    print(pezzo.id)
                    content_type, content_id = ContentType.objects.get_for_model(pezzo), pezzo.pk
                else:
                    orario = Orario(tariffa=float(dati.get("tariffa")),
                                    ore=timedelta(hours=int(dati.get("ore"))))
                    orario.save()
                    content_type, content_id = ContentType.objects.get_for_model(orario), orario.pk

                sottocampo.content_type = content_type
                sottocampo.content_id = content_id
                sottocampo.save()

                if target == "societa":
                    self.societa.sottocampi.add(sottocampo)
                    self.societa.save()
                else:
                    self.prodotto.sottocampi.add(sottocampo)
                    self.prodotto.save(no_slug=True)

                codice = genera_codici(request.session["codici_obj"])
                codici_obj = request.session["codici_obj"]
                codici_obj[codice] = {"pk": sottocampo.pk, "tipo": "Sottocampo"}
                request.session["codici_obj"] = codici_obj

                return Response({"success": True, "message": "sottocampo creato con successo",
                                 "dati": {
                                     "nome": sottocampo.nome,
                                     "totale": sottocampo.totale(),
                                     "tipo": sottocampo.tipo(),
                                     "codice": codice,
                                     "target": target
                                 }})
            else:
                return Response({"success": False, "message": "dati non validi"})

        else:
            return Response({"success": False, "message": "tipo non supportato"})
        
    def update(self, request):
        dati = request.data.get("dati")

        azione = dati.get("azione")
    
        # Aggiunge un sottocampo al campo : sottocampo, campo
        if azione == "aggiungi-sottocampi":
            stccmp_code = dati.get('sottocampo')  # codice del sottoccampo
            campo_code = dati.get('campo')  # codice del campo

            pk_stc, tipo_stc = request.session["codici_obj"][stccmp_code]["pk"], request.session["codici_obj"][stccmp_code]["tipo"]
            pk_cmp, tipo_cmp = request.session["codici_obj"][campo_code]["pk"], request.session["codici_obj"][campo_code]["tipo"]

            if tipo_stc != "Sottocampo" or tipo_cmp != "Campo":
                return Response({'success': False, 'message': 'Codici inesistenti'})
            
            try:
                Campo.objects.get(pk=pk_cmp).aggiungi_sottocampo(Sottocampo.objects.get(pk=pk_stc))
            except:
                return Response({'success': False, 'message': 'Impossibile aggiungere il sottocampo al campo'})
            
            # Aggiunta riuscita
            return Response({'success': True, 'message': 'Aggiunta effettuata con successo'})
        
        # Rimozione dei sottocampi ai campi
        if azione == "rimuovi-sottocampo":
            stccmp_code = dati.get('sottocampo')  # codice del sottoccampo
            campo_code = dati.get('campo')  # codice del campo

            pk_stc, tipo_stc = request.session["codici_obj"][stccmp_code]["pk"], request.session["codici_obj"][stccmp_code]["tipo"]
            pk_cmp, tipo_cmp = request.session["codici_obj"][campo_code]["pk"], request.session["codici_obj"][campo_code]["tipo"]

            if tipo_stc != "Sottocampo" or tipo_cmp != "Campo":
                return Response({'success': False, 'message': 'Codici inesistenti'})
            
            try:
                Campo.objects.get(pk=pk_cmp).rimuovi_sottocampo(Sottocampo.objects.get(pk=pk_stc))
            except:
                return Response({"success": False, "message": "Impossibile rimuovere il sottocampo"})
            
            # Rimozione riuscita
            return Response({"success": True, "message": "Rimuozione effettuata con successo"})
        
        # Rinomina un Sottocampo/Campo : codice, nome
        if azione == "rinomina":
            codice = dati.get("codice")
            nome = dati.get("nome")

            pk, tipo = request.session["codici_obj"][codice]["pk"], request.session["codici_obj"][codice]["tipo"]

            if tipo == "Sottocampo":
                model = Sottocampo.objects.get(pk=pk)
                
            elif tipo == "Campo":
                model = Campo.objects.get(pk=pk)
            else:
                return Response({'success': False, 'message': 'Codici inesistenti'})
            
            model.nome = nome
            model.save()
            
            return Response({'success': True, 'message': 'Nome aggiornato correttamente'})

    # Eliminazione di campi/sottocampi
    def delete(self, request):
        for codice in request.data.get("codici"):
            try:
                print(codice)
                pprint(request.session["codici_obj"])

                pk, tipo = request.session["codici_obj"][codice]["pk"], request.session["codici_obj"][codice]["tipo"]
                
                if tipo == "Sottocampo":
                    Sottocampo.objects.get(pk=pk).delete()
                else:
                    Campo.objects.get(pk=pk).delete()
            except:
                return Response({'success': False, 'message': f"Impossibile trovare l'elemento {tipo}"})

        return Response({'success': True, 'message': 'Eliminazione di tutti gli elementi'})
        
