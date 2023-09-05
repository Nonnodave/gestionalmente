Math.random()

window.addEventListener("DOMContentLoaded", () => {
    /* VARIABILI */
    const csrfToken = $('[name=csrfmiddlewaretoken]').val();

    const container = document.querySelector("#container");
    let tre_punti = document.querySelectorAll("#container > table > tbody > tr > td > svg");
    let link_prod = document.querySelectorAll("#container > table > tbody > tr > td.link-prod");

    let menu_trepunti = false;  // tre punti attivi

    /* FUNZIONI */

    // Funzione 'utility' per definire tutto (soprattutto quando si crea un nuovo prodotto)
    function definizioni_globali() 
    {
        tre_punti = document.querySelectorAll("#container > table > tbody > tr > td > svg");
        link_prod = document.querySelectorAll("#container > table > tbody > tr > td.link-prod");

        tre_punti.forEach(svg => svg.addEventListener("click", mostraMenuTrePunti));
        link_prod.forEach(cella => cella.addEventListener("click", (event) => window.location.href = cella.parentNode.getAttribute("url")));
        document.querySelectorAll("#container > table > tbody > tr > th.nome-prod").forEach(
            nome => nome.addEventListener("dblclick", () => funzioniTrePunti("rinomina", nome.parentNode) )
        );

        calcola_colore_importi();  // base.html
    }
    // Funzione 'utility' per inviare una richiesta di tipo UPDATE all'api
    function inviaApi(obj, func=() => {}) {
        let url_api = "/api/societa/";
        
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

    // Funzione 'utility' per gestire le azioni del menu a tendina
    function funzioniTrePunti(azione, target)
    {
        // target: row
        switch (azione) {
            case "rinomina":
                let nome = target.querySelector(".nome-prod");
                let vecchio_testo = nome.textContent;

                nome.contentEditable = "true";
                nome.setAttribute("contentEditable", "true");
                
                setTimeout(() => {
                    nome.focus();
                }, 100);

                let lambda_keydown = (event) => {
                    if (event.key == "Enter")
                    {
                        event.preventDefault();
                        nome.removeEventListener("blur", lambda_blur);

                        nome.setAttribute("contentEditable", "false");

                        if (nome.textContent == "")  // Il nome non può essere lasciato vuoto
                        {
                            lambda_blur(event);
                            return;
                        }

                        inviaApi({
                            tipo: "UPDATE",
                            dati: {
                                azione: "rinomina",
                                prodotto: target.getAttribute("codice"),
                                nome: nome.textContent
                            }
                        },
                        (risposta) => target.setAttribute("url", risposta["url"])
                        );                        

                        nome.removeEventListener("keydown", lambda_keydown);
                    }
                };

                let lambda_blur = (event) => {
                    // Lascio il tempo a keydown di agire
                    setTimeout(() => {
                        nome.contentEditable = "false";
                        nome.textContent = vecchio_testo;

                        nome.removeEventListener("blur", lambda_blur);
                        nome.removeEventListener("keydown", lambda_keydown);
                    }, 100);
                }

                nome.addEventListener("keydown", lambda_keydown);
                nome.addEventListener("blur", lambda_blur);

                break;
            
            case "cancella":
                let codice = target.getAttribute("codice");
                inviaApi({
                    tipo: "DELETE",
                    dati: {
                        codici: [codice]
                    }
                });
                target.remove();
                break;
        
            default:
                console.log("Azione non esistente");
                break;
        }
    }

    // Gestione del menu a tendina (posizione e listener)
    function mostraMenuTrePunti(event) {
        // currentTarget: svg
        let row = event.currentTarget.parentNode.parentNode;  // svg -> cella -> riga

        menu_trepunti = true;

        let div = document.createElement("div");
        for (let azione of ["rinomina", "cancella"])
        {
            let p = document.createElement("p");
            p.textContent = azione;
            p.addEventListener("mouseover", () => {p.style.backgroundColor = "rgba(128, 128, 128, 0.175)"});
            p.addEventListener("mouseout", () => {p.style.backgroundColor = "white"});
            p.addEventListener("mousedown", (event) => {lambda_chiudi_div(event); funzioniTrePunti(azione, row)});

            div.appendChild(p);
        }
        
        div.style.position = "absolute";
        div.style.left = event.clientX + "px";
        div.style.top = event.clientY + "px";
        div.style.zIndex = 1000;
        div.style.backgroundColor = "white";

        container.appendChild(div);

        let lambda_chiudi_div = (event) => {
            menu_trepunti = false;
            div.remove()
            window.removeEventListener("mousedown", lambda_chiudi_div);
        };
        window.addEventListener("mousedown", (event) => {if (event.target != div) lambda_chiudi_div(event);});
    }

    // Gestione del popUp ed invio dati per la creazione di nuovi prodotti
    function creaNuovoProdotto(event)
    {
        event.preventDefault()

        let dati = {}
        event.target.querySelectorAll("input").forEach(input => dati[input.name] = input.value);
        dati["modalita"] = "nuovo"
        inviaApi({
            dati: dati,
            tipo: "CREATE"
        }, (risposta) => {
            let prod_tr = document.querySelector("#popUp-element > div.example-tr-prod > table > tbody > tr").cloneNode(true);
            let dati = risposta["dati"];

            prod_tr.querySelectorAll(":not(:first-child):not(:last-child)").forEach((elem, indice) => {
                elem.querySelector("span").textContent = dati[indice];
            });

            prod_tr.setAttribute("codice", dati[6]);
            prod_tr.setAttribute("url", dati[7]);
                        
            document.querySelector("#tb-prodotti > tbody").appendChild(prod_tr);

            definizioni_globali();
        }
        );
        
        document.querySelector("#popup").chiudi();
    }

    /* EVENTI */

    // Menu a tendina 3 punti
    tre_punti.forEach(svg => svg.addEventListener("click", mostraMenuTrePunti));

    // Collegamento alla modifica del prodotti
    link_prod.forEach(cella => cella.addEventListener("click", (event) => window.location.href = cella.parentNode.getAttribute("url")));

    // Rinomina campo con doppio click
    document.querySelectorAll("#container > table > tbody > tr > th.nome-prod").forEach(
        nome => nome.addEventListener("dblclick", () => funzioniTrePunti("rinomina", nome.parentNode) )
    );
    
    // Creazione nuovo prodotto
    document.querySelector("#btn-nuovo-prod").addEventListener("click", () => {
        let elem = document.querySelector("#popUp-element > div.popUp-nuovo-prodotto").cloneNode(true);
        elem.querySelector("form").addEventListener("submit", creaNuovoProdotto);
        popUp(contenuto=elem);  // base.html
    });

    /* CODICE */
    calcola_colore_importi();  // base.html
});