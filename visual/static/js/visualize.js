/*          ---RULE---
    - camelCase for globals, sniper_case for locals
*/

Math.random()
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const COLORI = [
    "#7400B8",  // viola scuro  : 0
    "#6930C3",  // viola        : 1
    "#5E60CE",  // viola chiaro : 2
    "#5390D9",  // blu          : 3
    "#4EA8DE",  // azzurro      : 4
    "#48BFE3",  // celeste      : 5
    "#56CFE1",  // blu chiaro   : 6
    "#64DFDF",  // blu-verde    : 7
    "#72EFDD",  // verde acqua  : 8
    "#80FFDB",  // verde chiaro : 9
]

window.addEventListener("DOMContentLoaded", () => {
    /* --- DICHIARAZIONI --- */   
    // const
    const csrfToken = getCookie("csrftoken");

    const container = document.querySelector("#container");

    const divisore = document.querySelector("#divisore")
    const left = document.querySelector("#sottocampi");
    const rigth = document.querySelector("#campi");

    let sottocampi_list = document.querySelectorAll(".sottocampi-modello");
    const campi_div = document.querySelectorAll(".campi-list");

    const btn_cmp_slt = document.querySelector("#btn-campi-seleziona");
    const btn_cmp_del = document.querySelector("#btn-campi-elimina");
    const btn_cmp_anl = document.querySelector("#btn-campi-annulla");

    const btn_crea_cmp = document.querySelector("#btn-crea-campo");
    const btn_crea_stc = document.querySelector("#btn-crea-sottocampo");

    const cls_name_slt = "selezionato";  // Nome della classe per evidenziare la selezione del campo

    // Variabili
    // resize della finestra tramite divisore
    let resizing = false;  // Se è stato selezionato il divisore per il resize della finesta
    let mousePrec = 0;  // Ultima posizione del mouse
    let maxHeigth, maxWidth,  // Dimensioni della finestra
                     offset;  // larghezza minima di una finestra, altrimenti viene chiusa

    // drag sottotitoli per aggiunta ai campi
    let draggedElem = false;  // Se è stato selezionato o meno un elemento per il drag
    
    let finestra_slt = false;  // Finestra di selezione e cordinate mouse (se attiva)

    aggiorna_dim_finestra();  // Imposto i valori
    
    /* ---  FUNZIONI  ---  */
    // Funzione 'utility' per aggiornare il valore massimo del body
    function aggiorna_dim_finestra() {
        maxHeigth = container.offsetHeight;
        maxWidth = container.offsetWidth;
        offset = parseInt(maxWidth / 4);

        // Imposto l'altezza del divisore come la massima possibile
        divisore.style.height = maxHeigth + "px";
    }

    // Funzione 'utility' per impostare la grandezza delle finestre
    function resize_move(offset_left)
    {
        width = parseInt(divisore.style.width / 2);  // Metà della larghezza del divisore

        left.style.width = (offset_left - width) + "px";
        rigth.style.width = (maxWidth - offset_left - width) + "px";
    }

    // Funzione 'utility' per aggiungere un sottocampo ad un campo
    function aggiungi_sottocampo(stc, cmp) {
        // Controllo se è già presente
        let trovato = false
        cmp.querySelectorAll(".sottocampi-list > p").forEach(p => {
            console.log(p)
            if (p.getAttribute("codice") == stc.getAttribute("codice"))
            {
                p.querySelector("span").innerHTML = parseInt(p.querySelector("span").innerHTML) + 1;
                trovato = true;
                return;
            }
        });
        if (trovato)
            return;

        let stc_list = cmp.querySelector(".sottocampi-list");
        let par = document.createElement("p");
        par.classList.add("sottocampi-item");
        par.setAttribute("codice", stc.getAttribute("codice"));
        par.innerHTML = '<span class="quantita">1</span> x ' + stc.querySelector("p").innerHTML;

        stc_list.appendChild(par);
    }

    // Funzione 'utility' per filtrare una lista dato un attributo
    function filter(list, nome_attr, valore_attr) {
        let result = [];

        list.forEach(elem => {
            if (elem.getAttribute(nome_attr) == valore_attr)
                result.push(elem);
        })

        return result;
    }

    // Funzione 'utility' per inviare una richiesta di tipo UPDATE all'api
    function inviaApi(obj, func=() => {}) {
        let url_api = "/api/prodotto/";
        
        if (obj["tipo" != "CREATE"] && obj["tipo"] != "UPDATE" && obj["tipo"] != "DELETE")  // metodo non consentito
            return;

        $.ajax({
            url: url_api,
            method: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': csrfToken },
            dataType: 'json',
            data: JSON.stringify(obj),
            success: function(response) {
                // Handle success response
                console.log(response);
                func(response)
            },
            error: function(error) {
                console.log(error)
            },
        });
    }

    // Funzione 'utility' per inviare una richiesta di tipo UPDATE all'api
    function inviaUpdate(dati) {        
        inviaApi({
            tipo: "UPDATE",
            dati: dati
        });

        // $.ajax({
        //     url: url_api,
        //     method: 'POST',
        //     contentType: 'application/json',
        //     data: JSON.stringify({
        //         tipo: "UPDATE", dati
        //     }),
        //     success: function(response) {
        //         // Handle success response
        //     },
        //     error: function(error) {
        //         // Handle error response
        //     },
        // });
    }

    // Funzione 'utility' per gestire le chiamate ai vari mouseup
    function windowMouseUp(event) {
        if (stopResize(event)) return;
        if (disattivaFinestraSlt(event)) return;
    }

     // Funzione 'utility' per gestire le chiamate ai vari mousemove
    function windowMouseMove(event) {
        if (resize(event)) return;
        if (ridimensionaFinestraSlt(event)) return;
    }

    // Attiva la modalità (click sulla barra)
    function attivaResize(event) {
        resizing = true;
        left.style.pointerEvents = "none";
        rigth.style.pointerEvents = "none";
        event.preventDefault();
        
        mousePrec = event.clientX;
        aggiorna_dim_finestra();
        
        width_left = left.style.width;
        width_right = rigth.style.width;
    }

    // Disattiva la modalità quando il mouse viene rilasciato
    function stopResize()
    {
        if (resizing == true)
        {
            resizing = false;
            left.style.pointerEvents = "auto";
            rigth.style.pointerEvents = "auto";

            return true;
        }
    }

    // Regolazione dello spazio muovendo la barra
    function resize(event) {
        if (!resizing) {
            return false;
        }
        
        let mouse_pos = event.clientX;

        if (mousePrec <= offset || maxWidth - mousePrec <= offset) {
            // Comparsa delle finestre
            if (mouse_pos > offset || maxWidth - mouse_pos > offset)
                mousePrec = mouse_pos
        }
        else {
            // Scomparsa delle finestre
            if (mouse_pos <= offset)
            mouse_pos = 0;
            else if (maxWidth - mouse_pos <= offset)
            mouse_pos = maxWidth;
        }

        resize_move(mouse_pos);

        return true;
    }

    // Double Click sul divisore: setta le finestre al centro o mostra quella nascosta
    function doubleClick(event)
    {
        aggiorna_dim_finestra();

        // Riporto visibile la finestra di sinistra
        if (mousePrec <= offset)
            mousePrec = offset;

        // Riporto visibile la finesta di destra
        else if (maxWidth - mousePrec <= offset)
            mousePrec = maxWidth - offset;

        // Metto le finestre della stessa misura
        else
            mousePrec = parseInt(maxWidth / 2);
        
        // Visualizzo
        resize_move(mousePrec);
    }

    // Permette di selezionare i campi al click
    function selezionaCampi()
    {
        // Attivo i bottoni
        btn_cmp_anl.disabled = false;
        btn_cmp_del.disabled = false;

        // Creo gli eventListener sui campi
        document.querySelectorAll(".campi-list").forEach(campo => {            
            campo.addEventListener("click", () => {
                campo.classList.toggle(cls_name_slt);  // Aggiungo/tolgo la classe
            });
            campo.querySelectorAll("*").forEach(elem => elem.style.pointerEvents = "none")
        });

        btn_cmp_del.addEventListener("click", eliminaCampi);
        btn_cmp_anl.addEventListener("click", annullaSelezione);
        btn_cmp_slt.removeEventListener("click", selezionaCampi);
    }

    // Elimina i campi selezionati
    function eliminaCampi()
    {
        btn_cmp_del.removeEventListener("click", eliminaCampi);

        codici = []
        document.querySelectorAll(".campi-list").forEach(campo => {   
            if (campo.classList.contains(cls_name_slt))
                codici.push(campo.getAttribute("codice"));
        });
        
        inviaApi({
            tipo: "DELETE",
            codici: codici
        }, (response) => {
            if (response.success)
                for (codice of codici)
                    filter(campi_div, "codice", codice)[0].remove()
        });

        annullaSelezione();
    }

    // Annulla la selezione dei campi
    function annullaSelezione() {
        // Disattivo i bottoni
        btn_cmp_anl.disabled = true;
        btn_cmp_del.disabled = true;

        document.querySelectorAll(".campi-list").forEach(campo => {
            campo.classList.remove(cls_name_slt);
            campo.removeEventListener("click", () => {
                    console.log("premuto campo");
                    // Aggiungo/tolgo la classe
                    campo.classList.toggle(cls_name_slt);
                });

            campo.querySelectorAll("*").forEach(elem => elem.style.pointerEvents = "auto")
        });

        btn_cmp_slt.addEventListener("click", selezionaCampi);
    }

    // Apre il menu a tendina del campo su cui è chiamata
    function frecciaAprireTendina(event) {
        let header = event.currentTarget;

        if (event.target == header.querySelector("svg.penna-rinomina") || event.target == header.querySelector("h3"))  // Rinomina del campo
            return;

        if (header.querySelector("h3").getAttribute("contenteditable") == "true")  // Sto modificando il nome del campo
            return;

        // Apro la tendina
        header.parentNode.querySelector(".sottocampi-list").style.display = "block";

        // Imposto l'altra freccia
        header.querySelector("svg.freccia-aprire").style.display = "none";
        header.querySelector("svg.freccia-chiudere").style.display = "block";

        header.removeEventListener("click", frecciaAprireTendina);
        header.addEventListener("click", frecciaChiudereTendina);
    }

    // Chiude il menu a tendina del campo su cui è chiamata
    function frecciaChiudereTendina(event) {
        let header = event.currentTarget;  // .freccia-chiudere

        if (event.target == header.querySelector("svg.penna-rinomina") || event.target == header.querySelector("h3"))  // Rinomina del campo
            return;

        if (header.querySelector("h3").getAttribute("contenteditable") == "true")  // Sto modificando il nome del campo
            return;

        // Apro la tendina
        header.parentNode.querySelector(".sottocampi-list").style.display = "none";

        // Imposto l'altra freccia
        header.querySelector("svg.freccia-aprire").style.display = "block";
        header.querySelector("svg.freccia-chiudere").style.display = "none";

        header.removeEventListener("click", frecciaChiudereTendina);
        header.addEventListener("click", frecciaAprireTendina);
    }

    // Inizio del trascinamento del sottotitolo
    function dragStartStc(event) {
        draggedElem = true;  // un elemento è stato selezionato
        event.dataTransfer.setData("text/plain", this.getAttribute("codice"));
    }

    // Fine del trascinamento del sottocampo
    function dragEndStc(event) {
        draggedElem = false;
    }

    function dragOverCmp(event) {
        if (!draggedElem) return;

        event.preventDefault();  // per il browser
        console.log("over");
        this.style.borderColor = COLORI[0];
        this.style.borderWidth = "3px";
    }

    // Elemento entrato nel campo -> setto style
    function dragEnterCmp(event) {
        if (!draggedElem) return;
        
        event.preventDefault();  // per il browser
        console.log("enter");
    }

    // Elemento lascia il campo -> resetto style
    function dragLeaveCmp(event) {
        if (!draggedElem) return;
        
        console.log("leave");
        let target = event.currentTarget;
        target.style.borderColor = COLORI[5];
        target.style.borderWidth = "2px";
    }

    // Elemento rilasciato nel campo -> iniva la richiesta all'api
    function dropCmp(event) {
        if (!draggedElem) return;
        
        dragLeaveCmp(event);  // In caso in cui non venga eseguito

        // codici
        let codice_stc = event.dataTransfer.getData("text/plain");
        let codice_cmp = this.getAttribute("codice");
        let target = event.currentTarget;

        inviaUpdate({
            azione: "aggiungi-sottocampi",
            sottocampo: codice_stc,
            campo: codice_cmp
        });

        aggiungi_sottocampo(filter(sottocampi_list, "codice", codice_stc)[0], target);
    }

    // Funzione per rinominare il campo tramite la matita
    function rinominaCampo(event) {
        let target = event.currentTarget;  // header
        let h3 = target.parentNode.querySelector("h3");

        // Disabilito la tendina
        target.querySelectorAll("svg:not(.penna-rinomina)").forEach(svg => svg.style.pointerEvents = "none");

        let vecchio_testo = h3.innerHTML;
        h3.setAttribute("contentEditable", "true");

        setTimeout(() => {
            h3.focus();
        }, 100);
        
        let lamba_keydown = (event) => {
            console.log(event.key)
            if (event.key == "Enter")
            {
                event.preventDefault();
                h3.removeEventListener("blur", lamba_blur);  // Subito sennò interviene

                h3.setAttribute("contentEditable", "false");

                inviaUpdate({
                    azione: "rinomina",
                    codice: event.currentTarget.parentNode.parentNode.getAttribute("codice"),
                    nome: h3.innerHTML,
                });

                // Abilito la tendina
                target.querySelectorAll("svg:not(.penna-rinomina)").forEach(svg => svg.style.pointerEvents = "auto");

                h3.removeEventListener("keydown", lamba_keydown);
            }
        };
        h3.addEventListener("keydown", lamba_keydown);

        let lamba_blur = (event) => {
            // Aspetto un attimo così do il tempo a keydown di rimuoverlo (in caso sia stato attivato)
            setTimeout(() => {
                h3.contentEditable = "false";
                h3.innerHTML = vecchio_testo;

                // Abilito la tendina
                target.querySelectorAll("svg:not(.penna-rinomina)").style.pointerEvents = "auto";

                h3.removeEventListener("keydown", lamba_keydown);
                h3.removeEventListener("blur", lamba_blur);
            }, 100);
        };
        h3.addEventListener("blur", lamba_blur);        
    }

    function attivaFinestraSlt(event) {

        console.log("event:", event)
        console.log(event.currentTarget);
        console.log(event.target);

        if (finestra_slt == null)
            return false;

        // Funziona solo su #campi o #box-campi
        if (event.currentTarget != event.target && event.target != document.querySelector("#box-campi"))
            return false;

        // Inserisco la posizione corrente del mouse (posizione di partenza)
        console.log("client:", event.clientX, event.clientY);
        finestra_slt = [event.clientX, event.clientY];

        document.querySelector("#container").style.pointerEvents = "none";
        document.querySelector("#container").style.userSelect = "none";

        // Creo il div
        let div = document.createElement("div");
        div.id = "selezione-finestra"

        div.style.backgroundColor = "rgba(128, 128, 128, 0.175)";
        div.style.zIndex = 1;
        
        div.style.position = "absolute";
        div.style.left = finestra_slt[0] + "px";
        div.style.top = finestra_slt[1] + "px";

        console.log(div);
        div.style.width = "100px"; 
        div.style.height = "100px"; 

        console.log("finestra:", finestra_slt)

        document.querySelector("#container").appendChild(div);
    }

    function disattivaFinestraSlt(event) {
        if (finestra_slt == false)
            return;

        console.log("mouseup")

        // Imposto false la finestra
        finestra_slt = false;

        document.querySelector("#container").style.pointerEvents = "auto";
        document.querySelector("#container").style.userSelect = "auto";

        // Elimino tutti gli elementi all'interno del div
        let divs = document.querySelectorAll("#selezione-finestra");
        divs.forEach(div => div.remove());

        // Richiamo seleziona
        selezionaCampi();

        return true;
    }

    function ridimensionaFinestraSlt(event) {
        if (finestra_slt == false)
            return false;

        if (event.clientX < parseInt(left.style.width))  // coordinata non valida, non posso andare nei sottocampi
            return false;

        console.log(event.clientX, )

        let div = document.querySelector("#selezione-finestra");

        if (event.clientX < finestra_slt[0])
            {div.style.left = event.clientX + "px"; console.log("cambio x")}
        
        if (event.clientY < finestra_slt[1])
            {div.style.top = event.clientY + "px"; console.log("cambio y")}

        div.style.width = Math.abs(event.clientX - finestra_slt[0]) + "px";
        div.style.height = Math.abs(event.clientY - finestra_slt[1]) + "px";

        // console.log("finestra:", finestra_slt, "client:", [event.clientX, event.clientY], "dim:", [div.style.left, div.style.top]);

        // Controllo se sono sopra un campo
        document.querySelectorAll(".campi-list").forEach(campo => {
            let centro = [
                campo.offsetLeft + campo.offsetWidth / 2,
                campo.offsetTop + campo.offsetHeight / 2
            ]
            
            // console.log("centro:", centro, "div:", [div.style.left, div.style.top])
            if (
                Math.min(finestra_slt[0], div.style.left) <= centro[0] &&
                Math.max(finestra_slt[0], div.style.left) >= centro[0] &&
                Math.min(finestra_slt[1], div.style.top) <= centro[1] &&
                Math.max(finestra_slt[1], div.style.top) >= centro[1]
            )
                campo.classList.add(cls_name_slt);
        })
        let elem = document.elementFromPoint(finestra_slt[0], finestra_slt[1]);
        if (elem.classList.contains("campi-list"))
            elem.classList.add(cls_name_slt);  // lo seleziono

        return true;
    }

    /* --- EVENTI --- */
    // Resize della finestra
    $(window).on("resize", () => {
        mousePrec = parseInt(maxWidth / 2);
        doubleClick();
    });

    // resize
    divisore.addEventListener("mousedown", attivaResize);
    divisore.addEventListener("dblclick", doubleClick);
    window.addEventListener("mousemove", windowMouseMove);
    window.addEventListener("mouseup", windowMouseUp);

    // drag sottocampi
    sottocampi_list.forEach(stc => {
        stc.addEventListener("dragstart", dragStartStc);
        stc.addEventListener("dragend", dragEndStc);
    });
    campi_div.forEach(cmp => {
        cmp.addEventListener('dragover', dragOverCmp);  // Elemento sul campo
        cmp.addEventListener('dragenter', dragEnterCmp);  // Elemento entrato nel campo
        cmp.addEventListener('dragleave', dragLeaveCmp);  // Elemento esce dal campo
        cmp.addEventListener('drop', dropCmp);  // Elemento rilasciato nel campo
    })

    // Bottone di selezione per i campi
    btn_cmp_slt.addEventListener("click", selezionaCampi);

    // Gestione della tendina dei campi (freccia)
    document.querySelectorAll(".campo-header").forEach(header => {
        header.querySelector("svg.freccia-aprire").style.display = "none";
        header.querySelector("svg.freccia-chiudere").style.display = "block";

        header.addEventListener("click", frecciaChiudereTendina);
    })

    // Penna per rinominare il campo
    document.querySelectorAll("#box-campi > div > div.flex.campo-header > svg.penna-rinomina").forEach(penna => {
        penna.addEventListener("click", rinominaCampo);
    });

    // Doppio click (sul nome) per rinominare il campo
    document.querySelectorAll("#box-campi > div > div.flex.campo-header > h3").forEach(h3 => {
        h3.addEventListener("dblclick", rinominaCampo);
    });

    // Comparsa/scomparsa cestino sottocampi
    sottocampi_list.forEach(stc => stc.addEventListener("mouseover", () => stc.querySelector("svg").style.display = "block"));
    sottocampi_list.forEach(stc => stc.addEventListener("mouseout", () => stc.querySelector("svg").style.display = "none"));

    // Gestione eliminazione dei sottocampi
    document.querySelectorAll(".pattume-sottocampi").forEach(svg => {
        svg.addEventListener("click", (event) => {
            event.preventDefault();

            let codice = svg.parentNode.getAttribute("codice");

            inviaApi({
                tipo: "DELETE",
                codici: [codice]
            }, () => {svg.parentNode.remove()});
        });
    });

    // Bottone per creare campi
    btn_crea_cmp.addEventListener("click", () => {
        elem = document.querySelector("#popUp-element > div.popUp-nuovo-campo").cloneNode(true);
        elem.querySelector("form").addEventListener("submit", (event) => {
            event.preventDefault();
            let form = event.currentTarget;

            if (!form.checkValidity())
                return;

            let dati = {}
            form.querySelectorAll("input:not([type='submit'])").forEach(input => dati[input.name] = input.value);

            inviaApi({
                tipo: "CREATE",
                dati: {
                    tipo: "campo",
                    form: dati
                }
            }, (response) => {
                document.querySelector("#popup").chiudi();
                let campo = document.querySelector("#popUp-element > div.nuovo-campo > div").cloneNode(true);

                campo.setAttribute("codice", response.dati["codice"]);
                document.querySelector("div > h3").textContent = response.dati["nome"];

                let div = document.querySelector("#box-campi");
                div.insertBefore(campo, div.children[div.children.length-1]);
            });
        });

        popUp(contenuto=elem);
    });

    // Bottone per creare sottocampi
    btn_crea_stc.addEventListener("click", () => {
        elem = document.querySelector("#popUp-element > div.popUp-nuovo-sottocampo").cloneNode(true);
        
        // Disabilito gli input dell'orario (default = pezzo)
        elem.querySelector("#form-orario").querySelectorAll("input").forEach(input => input.disabled = true);

        // Aggiungo l'evento per il submit e l'invio della richiesta
        elem.querySelector("form").addEventListener("submit", (event) => {
            event.preventDefault();
            let form = event.currentTarget;

            if (!form.checkValidity())
                return;

            let dati = {};
            form.querySelectorAll("input:not([type='submit']):not([name='target']):not([name='tipologia']):not([disabled])").forEach(
                input => dati[input.name] = input.value );
                
            inviaApi({
                tipo: "CREATE",
                dati: {
                    tipo: "sottocampo",
                    tipologia: elem.querySelector(".tipologia-hidden").value,
                    target: elem.querySelector(".target-hidden").value,
                    form: dati
                }
            }, (response) => {
                document.querySelector("#popup").chiudi();

                let sottocampo = document.querySelector("#popUp-element > div.nuovo-sottocampo > div").cloneNode(true);
                sottocampo.setAttribute("codice", response.dati["codice"]);
                sottocampo.classList.add("sottocampo-modello");

                let p = document.createElement("p");
                p.innerHTML = response.dati["nome"] + ' | <span class="importo">' + response.dati["totale"] + '</span>€/' + response.dati["tipo"]
                
                let pattume = sottocampo.querySelector("svg");
                
                // EventListener
                sottocampo.addEventListener("dragstart", dragStartStc);
                sottocampo.addEventListener("dragend", dragEndStc);
                p.addEventListener("mouseover", () => pattume.style.display = "block");
                p.addEventListener("mouseout", () => pattume.style.display = "none");

                sottocampo.insertBefore(p, pattume);
                
                let div;  // sempre alla fine
                if (response.dati["target"] == "societa")
                    div = document.querySelector("#sottocampi > div > div.sottocampi-societa");
                else
                    div = document.querySelector("#sottocampi > div > div.sottocampi-prodotto");

                div.appendChild(sottocampo);

                sottocampi_list = document.querySelector(".sottocampi-item");

                // Proprietà
                calcola_colore_importi();

                sottocampo.addEventListener("mouseover", () => sottocampo.querySelector("svg").style.display = "block");
                sottocampo.addEventListener("mouseout", () => sottocampo.querySelector("svg").style.display = "none");

                sottocampo.querySelector("svg").addEventListener("click", (event) => {
                    event.preventDefault();
        
                    inviaApi({
                        tipo: "DELETE",
                        codici: [response.dati["codice"]]
                    }, () => {sottocampo.remove()});
                });

            });
        });
        
        popUp(contenuto=elem);
    })

    // // Selezione tramite finestra
    // document.querySelector("#campi").addEventListener("mousedown", attivaFinestraSlt);
    // window.addEventListener("mousemove", windowMouseMove);
    // window.addEventListener("mouseup", windowMouseUp);

    /* --- CODICE --- */
    // Imposto le due finestre perfettamente al centro
    mousePrec = parseInt(maxWidth / 2);
    doubleClick();

    calcola_colore_importi();  // base.html
});

/* GLOBALE */

const btn_get_active_class_name = "btn-success";
const btn_get_inactive_class_name = "btn-outline-danger"

// Funzione 'utility popup' per gestire l'input change nella selezione della tipologia di sottocampo
function getInputChange(elem, classe, swap=true) {
    if (elem.classList.contains(btn_get_inactive_class_name))  // il button premuto non è attivo
    {
        let btn_hidden = document.querySelector("#popup > div > #form-dati > input." + classe);
        let btn_attivo = elem.parentNode.querySelector("." + btn_get_active_class_name);
        let btn_inattivo = elem.parentNode.querySelector("." + btn_get_inactive_class_name);

        let form_pezzo = document.querySelector("#popup > div > #form-dati > #form-pezzo");
        let form_orario = document.querySelector("#popup > div > #form-dati > #form-orario");

        btn_hidden.setAttribute("value", elem.getAttribute("value"));

        btn_attivo.classList.toggle(btn_get_active_class_name);
        btn_inattivo.classList.toggle(btn_get_active_class_name);

        btn_attivo.classList.toggle(btn_get_inactive_class_name);
        btn_inattivo.classList.toggle(btn_get_inactive_class_name);

        // Swappo il form tra pezzo e orario
        if (swap)
        {
            if (btn_attivo.getAttribute("value") == "pezzo")  // attivo orario
            {
                form_orario.style.display = "block";
                form_orario.querySelectorAll("input").forEach(input => input.disabled = false);

                form_pezzo.style.display = "none";
                form_pezzo.querySelectorAll("input").forEach(input => input.disabled = true);
            }
            else // attivo pezzo
            {
                form_pezzo.style.display = "block";
                form_pezzo.querySelectorAll("input").forEach(input => input.disabled = false);
    
                form_orario.style.display = "none";
                form_orario.querySelectorAll("input").forEach(input => input.disabled = true);
            }
        }
        else
        {
            document.querySelector("#popup > div > p").textContent = btn_inattivo.getAttribute("testo");
        }
    }
}