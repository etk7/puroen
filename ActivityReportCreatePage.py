from django.db import models 

class ActivityReport:
    creatre_date = models.DateTime()
    group_name = models.Char()
    contents = models.Textbox ()  