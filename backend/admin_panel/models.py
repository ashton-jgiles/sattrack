from django.db import models


class Administrator(models.Model):
    username    = models.OneToOneField(
                      'datasets.User',
                      on_delete=models.CASCADE,
                      primary_key=True,
                      db_column='username',
                      to_field='username'
                  )
    employee_id = models.IntegerField()

    class Meta:
        managed  = False
        db_table = 'administrator'

    def __str__(self):
        return f"Admin: {self.username_id}"


class DataAnalyst(models.Model):
    username    = models.OneToOneField(
                      'datasets.User',
                      on_delete=models.CASCADE,
                      primary_key=True,
                      db_column='username',
                      to_field='username'
                  )
    employee_id = models.IntegerField()

    class Meta:
        managed  = False
        db_table = 'data_analyst'

    def __str__(self):
        return f"Analyst: {self.username_id}"


class Scientist(models.Model):
    username   = models.OneToOneField(
                     'datasets.User',
                     on_delete=models.CASCADE,
                     primary_key=True,
                     db_column='username',
                     to_field='username'
                 )
    profession = models.CharField(max_length=100)

    class Meta:
        managed  = False
        db_table = 'scientist'

    def __str__(self):
        return f"Scientist: {self.username_id}"


class Amateur(models.Model):
    username  = models.OneToOneField(
                    'datasets.User',
                    on_delete=models.CASCADE,
                    primary_key=True,
                    db_column='username',
                    to_field='username'
                )
    interests = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'amateur'

    def __str__(self):
        return f"Amateur: {self.username_id}"
