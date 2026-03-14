from django.db import models


class User(models.Model):
    username     = models.CharField(max_length=50, primary_key=True)
    password     = models.CharField(max_length=255)
    full_name    = models.CharField(max_length=100)
    level_access = models.IntegerField()

    class Meta:
        managed  = False
        db_table = 'user'

    def __str__(self):
        return self.username


class Dataset(models.Model):
    dataset_id    = models.AutoField(primary_key=True)
    dataset_name  = models.CharField(max_length=150)
    description   = models.TextField(null=True, blank=True)
    creation_date = models.DateField()
    file_size     = models.CharField(max_length=20, null=True, blank=True)
    source        = models.CharField(max_length=50)
    source_url    = models.CharField(max_length=500)
    pull_frequency = models.CharField(max_length=20, null=True, blank=True)
    last_pulled   = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=10, default='pending')

    class Meta:
        managed  = False
        db_table = 'dataset'

    def __str__(self):
        return self.dataset_name


class Uploads(models.Model):
    uploaded_by = models.ForeignKey(
                      'admin_panel.Administrator',
                      on_delete=models.CASCADE,
                      db_column='uploaded_by',
                      to_field='username'
                  )
    dataset     = models.ForeignKey(
                      Dataset,
                      on_delete=models.CASCADE,
                      db_column='dataset_id'
                  )
    uploaded_at = models.DateTimeField()

    class Meta:
        managed         = False
        db_table        = 'uploads'
        unique_together = [['uploaded_by', 'dataset']]

    def __str__(self):
        return f"{self.uploaded_by} uploaded {self.dataset}"


class Reviews(models.Model):
    reviewed_by = models.ForeignKey(
                      'admin_panel.DataAnalyst',
                      on_delete=models.CASCADE,
                      db_column='reviewed_by',
                      to_field='username'
                  )
    dataset     = models.ForeignKey(
                      Dataset,
                      on_delete=models.CASCADE,
                      db_column='dataset_id'
                  )
    reviewed_at = models.DateTimeField()

    class Meta:
        managed         = False
        db_table        = 'reviews'
        unique_together = [['reviewed_by', 'dataset']]

    def __str__(self):
        return f"{self.reviewed_by} reviewed {self.dataset}"


class Views(models.Model):
    username         = models.ForeignKey(
                           User,
                           on_delete=models.CASCADE,
                           db_column='username',
                           to_field='username'
                       )
    dataset          = models.ForeignKey(
                           Dataset,
                           on_delete=models.CASCADE,
                           db_column='dataset_id'
                       )
    downloads        = models.IntegerField(default=0)
    views            = models.IntegerField(default=0)
    interaction_date = models.DateField()

    class Meta:
        managed         = False
        db_table        = 'views'
        unique_together = [['username', 'dataset', 'interaction_date']]

    def __str__(self):
        return f"{self.username} — {self.dataset}"
