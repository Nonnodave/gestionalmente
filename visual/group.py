from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from visual.models import CustomUser, Societa, Campo, Sottocampo

# CONTENT TYPE
content_type_user = ContentType.objects.get(app_label='visual', model='CustomUser')
content_type_societa = ContentType.objects.get(app_label='visual', model='Societa')
content_type_campo = ContentType.objects.get(app_label='visual', model='Campo')
content_type_sottocampo = ContentType.objects.get(app_label='visual', model='Sottocampo')


# PERMESSI : create, delete, change, view

# # Utenti
# admit_utenti_perm = Permission.objects.get_or_create(
#     codename = "create_utenti_perm",
#     name = "Aggiunta Utenti Permission",
#     content_type = None
# )

# erase_utenti_perm = Permission.objects.get_or_create(
#     codename = "delete_utenti_perm",
#     name = "Cancellazione Utenti Permission",
#     content_type = None
# )

# # puoi modificare i permessi fino al tuo permesso più alto
# change_utenti_perm = Permission.objects.get_or_create(  # cambiare i permessi
#     codename = "change_utenti_perm",
#     name = "Modifica Utenti Permission",
#     content_type = None
# )

# view_utenti_perm = Permission.objects.get_or_create(  # vedere gli utenti della socità
#     codename = "view_utenti_perm",
#     name = "Visualizzazione Utenti Permission",
#     content_type = None
# )

# Societa
create_societa_perm = Permission.objects.get_or_create(
    codename = "create_societa_perm",
    name = "Creazione Societa Permission",
    content_type = content_type_societa
)

delete_societa_perm = Permission.objects.get_or_create(
    codename = "delete_societa_perm",
    name = "Cancellazione Societa Permission",
    content_type = content_type_societa
)

change_societa_perm = Permission.objects.get_or_create(
    codename = "change_societa_perm",
    name = "Modifica Societa Permission",
    content_type = content_type_societa
)

view_societa_perm = Permission.objects.get_or_create(
    codename = "view_societa_perm",
    name = "Visualizzazione Società Permission",
    content_type = content_type_societa
)

# # Prodotto
# create_prodotto_perm = Permission.objects.get_or_create(
#     codename = "create_prodotto_perm",
#     name = "Creazione Prodotto Permission",
#     content_type = None
# )

# delete_prodotto_perm = Permission.objects.get_or_create(
#     codename = "delete_prodotto_perm",
#     name = "Cancellazione Prodotto Permission",
#     content_type = None
# )

# change_prodotto_perm = Permission.objects.get_or_create(
#     codename = "change_prodotto_perm",
#     name = "Modifica Prodotto Permission",
#     content_type = None
# )

# view_prodotto_perm = Permission.objects.get_or_create(
#     codename = "view_prodotto_perm",
#     name = "Visualizzazione Prodotto Permission",
#     content_type = None
# )

# # Campo
# create_campo_perm = Permission.objects.get_or_create(
#     codename = "create_campo_perm",
#     name = "Creazione Campo Permission",
#     content_type = None
# )

# delete_campo_perm = Permission.objects.get_or_create(
#     codename = "delete_campo_perm",
#     name = "Cancellazione Campo Permission",
#     content_type = None
# )

# change_campo_perm = Permission.objects.get_or_create(
#     codename = "change_campo_perm",
#     name = "Modifica Campo Permission",
#     content_type = None
# )

# view_campo_perm = Permission.objects.get_or_create(
#     codename = "view_campo_perm",
#     name = "Visualizzazione Campo Permission",
#     content_type = None
# )

# # Sottocampo
# create_sottocampo_perm = Permission.objects.get_or_create(
#     codename = "create_sottocampo_perm",
#     name = "Creazione Sottocampo Permission",
#     content_type = None
# )

# delete_sottocampo_perm = Permission.objects.get_or_create(
#     codename = "delete_sottocampo_perm",
#     name = "Cancellazione Sottocampo Permission",
#     content_type = None
# )

# change_sottocampo_perm = Permission.objects.get_or_create(
#     codename = "change_sottocampo_perm",
#     name = "Modifica Sottocampo Permission",
#     content_type = None
# )

# view_sottocampo_perm = Permission.objects.get_or_create(
#     codename = "view_sottocampo_perm",
#     name = "Visualizzazione Sottocampo Permission",
#     content_type = None
# )

# gerarchia = {  # codename: level
    
# }

# GRUPPI
crud_societa = Group.objects.get_or_create(name="CrudSocieta")
crud_societa.permissions.add(create_societa_perm, delete_societa_perm, change_societa_perm, view_societa_perm)