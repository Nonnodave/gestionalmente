let btn_pezzo = document.querySelector("#get-pezzo");
let btn_orario = document.querySelector("#get-orario");
let btn_hidden = document.querySelector("#get-hidden");

let btn_get_active_class_name = "btn-success";
let btn_get_inactive_class_name = "btn-light"

function getInputChange(elem) {
    if (elem.classList.contains(btn_get_inactive_class_name))  // il button premuto non è attivo
    {
        btn_hidden.value = elem.value;
        elem.classList.add(btn_get_active_class_name);
        elem.classList.remove(btn_get_inactive_class_name);

        // Rimuovo la classe al bottone precedente
        if (elem.id === btn_pezzo.id)
        {
            btn_orario.classList.remove(btn_get_active_class_name);
            btn_orario.classList.add(btn_get_inactive_class_name);
        }
        else
        {
            btn_pezzo.classList.remove(btn_get_active_class_name);
            btn_pezzo.classList.add(btn_get_inactive_class_name);
        }
    }
}
