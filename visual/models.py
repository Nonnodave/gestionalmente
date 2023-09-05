
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, MinimumLengthValidator

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.text import slugify
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator

from decimal import Decimal
from pprint import pprint

# Campo primario
class Sottocampo(models.Model):
    nome = models.CharField(max_length=120)
    # ruolo = models.CharField(max_length=10, choices=(
    #     ("Guadango", "guadagno"), ("Spesa", "spesa")
    # ))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    content_id = models.PositiveIntegerField(null=True)
    oggetto = GenericForeignKey("content_type", "content_id")

    def sottocampo_primario(self):
        # try:
        #     return self.pezzo
        # except:
        #     try:
        #         return self.orario
        #     except:
        #         return False

        return self.oggetto if self.oggetto is not None else False

    def tipo(self):
        if self.oggetto:
            return self.sottocampo_primario().tipo()
            
    def totale(self):
        if (self.oggetto):
            totale = self.oggetto.totale()
            print("totale:", totale)

            if isinstance(totale, str):  # sottocampo invalido
                return totale
            else:
                return totale
        else:
            return "..."  # totale invalido, non c'è il sottocampo

    def info(self):
        if (self.oggetto):
            return self.oggetto.totale()
        else:
            print("Sottocampo non ancora settato")
            return "..."

    def __str__(self) -> str:
        return f"{self.nome}"
    
class Societa(models.Model):
    nome = models.CharField(max_length=120)
    # nome_slug = models.SlugField(blank=True)  # Nome calcolato da quello dell'utente (solo minuscole, con trattini), serve per l'url univoco

    sottocampi = models.ManyToManyField(Sottocampo, related_name="societa")
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    # def save(self, no_slug=False, *args, **kwargs):
    #     if not no_slug:
    #         self.calcola_nome_formale()   # Calcolo lo slug

    #     super().save(*args, **kwargs)

    # def calcola_nome_formale(self, save=False):
    #     slug = slugify(self.nome)

    #     if Prodotto.objects.filter(nome_slug=slug).exists():  # Lo slug esiste, ci aggiungo un numero
    #         num = 1
    #         while True:
    #             new_slug = slug + "-" + str(num)

    #             if not Prodotto.objects.filter(nome_slug=new_slug).exists():  # Controllo se va bene
    #                 break

    #             num += 1
            
    #         self.nome_slug = slug + "-" + str(num)
    #     else:
    #         self.nome_slug = slug

    #     if save:
    #         self.save(no_slug=True)

    def __str__(self) -> str:
        return f"{self.nome}"

# Utenti
class CustomUserManagment(BaseUserManager):
    def create_user(self, email, password=None, **campi_extra):
        if not email:
            raise ValueError("L'email deve essere specificata")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **campi_extra)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
# # EMAIL, nome, cognome [is_active, data_creazione]
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # campo univoco
    nome = models.CharField(max_length=120)
    cognome = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    data_creazione = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(default=timezone.now)

    objects = CustomUserManagment()
    
    # Quando viene eliminata la Societa, viene settato a NULL (non è obbligatorio specificare una società in fare di registrazione)
    societa = models.ForeignKey(Societa, on_delete=models.SET_NULL, related_name="utenti", null=True, blank=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "cognome"]

    def update_last_login(self):
        self.ultimo_login = timezone.now()
        self.save()

    def __str__(self) -> str:
        return f"nome: {self.nome}, cognome: {self.cognome},  email: {self.email} societa: {self.societa.__str__()}"
    
'''
SOTTOCAMPO <- OneToOne -> Pezzo | Orario
CAMPO <- ManyToMany -> SOTTOCAMPO
'''

# Sotto campo pripario
class Pezzo(models.Model):
    costo = models.DecimalField(decimal_places=1, max_digits=8, validators=[MinValueValidator(Decimal("0.0"))])
    numero = models.IntegerField(default=1)
    # sottocampo = models.OneToOneField(Sottocampo, models.CASCADE, related_name="pezzo")

    def tipo(self):
        return "pezzo"
    
    def isNone(self):
        return self.costo == None or self.numero == None
    
    def totale(self):
        if self.isNone():  # totale invalido
            return "..."
        
        return float(self.costo / self.numero)
    
    def pezzi(self, numero_pezzi):
        return float(self.costo / numero_pezzi)
    
    def info(self):
        if self.costo == None:
            return "...", self.numero
        return self.costo, self.numero

    def __str__(self) -> str:
        return f"{self.numero} pezzi a {self.costo} €/pezzo"
    
# Sotto campo primario
class Orario(models.Model):
    tariffa = models.DecimalField(decimal_places=1, max_digits=8, validators=[MinValueValidator(Decimal("0.0"))])
    ore = models.DurationField()  # datetime.timedelta
    # sottocampo = models.OneToOneField(Sottocampo, models.CASCADE, related_name="orario")

    def tipo(self):
        return "ora"
    
    def isNone(self):
        return self.tariffa == None or self.ore == None
    
    def get_formato_orario(self):
        return Decimal(self.ore.days * 24) + Decimal(self.ore.seconds / 3600)
    
    def totale(self):
        if self.isNone():  # totale invalido
            return "..."
        
        print(float(self.tariffa / self.get_formato_orario()))
        return float(self.tariffa / self.get_formato_orario())
    
    def orari(self, numero_ore):
        return float(self.tariffa * numero_ore)
    
    def info(self):
        tariffa, ore = self.tariffa, self.ore

        if tariffa == None:  # None
            tariffa = "..."

        if ore == None:  # None
            ore = "..."

        return tariffa, ore

    def __str__(self) -> str:
        return f"{naturaltime(self.ore)} ore a {self.tariffa} €/ora"

class Prodotto(models.Model):
    nome = models.CharField(max_length=120)
    nome_slug = models.SlugField(blank=True)  # Nome calcolato da quello dell'utente (solo minuscole, con trattini), serve per l'url univoco

    data_creazione = models.DateTimeField(auto_now_add=True)
    data_ultima_modifica = models.DateTimeField(auto_now=True)

    societa = models.ForeignKey(Societa, on_delete=models.CASCADE, related_name="prodotti")

    sottocampi = models.ManyToManyField(Sottocampo, related_name="prodotto")

    def save(self, no_slug=False, *args, **kwargs):
        if not no_slug:
            self.calcola_nome_formale()   # Calcolo lo slug

        super().save(*args, **kwargs)

    def calcola_nome_formale(self, save=False):
        slug = slugify(self.nome)

        if self.societa.prodotti.filter(nome_slug=slug).exists():  # Lo slug esiste, ci aggiungo un numero
            num = 1
            new_slug = slug + "-" + str(num)
            while Prodotto.objects.filter(nome_slug=new_slug).exists():

                new_slug = slug + "-" + str(num)
                print("controllo:", new_slug, Prodotto.objects.filter(nome_slug=new_slug).exists())

                num += 1
            
            self.nome_slug = slug + "-" + str(num)
        else:
            self.nome_slug = slug

        if save:
            self.save(no_slug=True)

    def __iadd__(self, other):
        for campo in other.campi.all():
            campo = campo.copy()
            campo.prodotto = self
            campo.save()

    def totale(self):
        totale = {
            "pezzo": 0,
            "ora": 0
        }

        try:
            for campo in self.campi.all():
                value = campo.totale()
                if (value == "..."):  # totale invalido
                    return "..."
        
                for key in totale:
                    if key not in value:
                        continue

                    totale[key] += value[key]
        except:
            totale = "..."
        finally:
            return totale

    def __str__(self) -> str:
        return f"{self.nome}"


class Campo(models.Model):
    nome = models.CharField(max_length=120)  # Nome inserito dall'utente

    sottocampi = models.ManyToManyField(Sottocampo, related_name="sottocampi", through="CampoSottocampo")
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, related_name="campi")

    def aggiungi_sottocampo(self, sottocampo, quantita=1):
        sottocampo, creato = CampoSottocampo.objects.get_or_create(sottocampo=sottocampo, campo=self)

        if not creato:  # già inserito
            sottocampo.quantita += quantita  # aggiungo le quantità
            sottocampo.save()

        self.prodotto.data_ultima_modifica = timezone.now()  # aggiorno la data del prodotto
        self.prodotto.save(no_slug=True)

    def rimuovi_sottocampo(self, sottocampo):
        rels = CampoSottocampo.objects.filter(campo=self, sottocampo=sottocampo)

        if rels.exists():
            for rel in rels:
                rel.delete()

            self.prodotto.data_ultima_modifica = timezone.now()
            self.prodotto.save(no_slug=True)

    def totale(self):
        totale = {}
        for rel in CampoSottocampo.objects.filter(campo=self):
            tipo = rel.sottocampo.tipo()

            if tipo not in totale:
                totale[tipo] = 0

            if totale[tipo] == "...":  # totale invalido
                return
            
            valore = rel.sottocampo.totale()
            if (valore == "..."):  # totale invalido
                totale[tipo] = "..."
                continue

            totale[tipo] += valore * rel.quantita

        return totale

    def save(self, *args, **kwargs):
        self.prodotto.data_ultima_modifica = timezone.now()  # aggiorno la data del prodotto
        self.prodotto.save(no_slug=True)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.nome}"

# Relazione, mi serve per gestire la quantita
class CampoSottocampo(models.Model):
    sottocampo = models.ForeignKey(Sottocampo, on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    quantita = models.IntegerField(default=1)  # numero di sottocampi dello stesso tipo

    def __str__(self) -> str:
        return f"stc: {self.sottocampo}, cmp: {self.campo}, quantita: {self.quantita}"
    