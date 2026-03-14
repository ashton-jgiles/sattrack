from django.db import models


class SatelliteOwner(models.Model):
    owner_id      = models.AutoField(primary_key=True)
    owner_name    = models.CharField(max_length=150)
    owner_phone   = models.CharField(max_length=20, null=True, blank=True)
    owner_address = models.CharField(max_length=255, null=True, blank=True)
    country       = models.CharField(max_length=100, null=True, blank=True)
    operator      = models.CharField(max_length=150, null=True, blank=True)
    owner_type    = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'satellite_owner'

    def __str__(self):
        return self.owner_name


class LaunchSite(models.Model):
    location  = models.CharField(max_length=100, primary_key=True)
    weather   = models.CharField(max_length=100, null=True, blank=True)
    site_name = models.CharField(max_length=150, null=True, blank=True)
    country   = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'launch_site'

    def __str__(self):
        return self.site_name or self.location


class LaunchVehicle(models.Model):
    vehicle_id       = models.AutoField(primary_key=True)
    vehicle_name     = models.CharField(max_length=100)
    manufacturer     = models.CharField(max_length=100, null=True, blank=True)
    reusable         = models.BooleanField(null=True, blank=True)
    country          = models.CharField(max_length=100, null=True, blank=True)
    payload_capacity = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'launch_vehicle'

    def __str__(self):
        return self.vehicle_name


class LaunchedFrom(models.Model):
    vehicle     = models.ForeignKey(
                      LaunchVehicle,
                      on_delete=models.CASCADE,
                      db_column='vehicle_id'
                  )
    location    = models.ForeignKey(
                      LaunchSite,
                      on_delete=models.CASCADE,
                      db_column='location',
                      to_field='location'
                  )
    launch_date = models.DateField()

    class Meta:
        managed         = False
        db_table        = 'launched_from'
        unique_together = [['vehicle', 'location', 'launch_date']]

    def __str__(self):
        return f"{self.vehicle} from {self.location} on {self.launch_date}"


class CommunicationStation(models.Model):
    location                = models.CharField(max_length=100, primary_key=True)
    name                    = models.CharField(max_length=100)
    communication_frequency = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'communication_station'

    def __str__(self):
        return self.name


class Satellite(models.Model):
    satellite_id      = models.AutoField(primary_key=True)
    name              = models.CharField(max_length=100)
    description       = models.TextField(null=True, blank=True)
    last_contact_time = models.DateTimeField(null=True, blank=True)
    owner             = models.ForeignKey(
                            SatelliteOwner,
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            db_column='owner_id'
                        )
    dataset           = models.ForeignKey(
                            'datasets.Dataset',
                            on_delete=models.PROTECT,
                            db_column='dataset_id'
                        )
    username          = models.ForeignKey(
                            'datasets.User',
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            db_column='username',
                            to_field='username'
                        )
    orbit_type        = models.CharField(max_length=10)
    norad_id          = models.CharField(max_length=10, null=True, blank=True)
    object_id         = models.CharField(max_length=20, null=True, blank=True)
    classification    = models.CharField(max_length=1, default='U')

    class Meta:
        managed  = False
        db_table = 'satellite'

    def __str__(self):
        return self.name


class Trajectory(models.Model):
    dataset           = models.ForeignKey(
                            'datasets.Dataset',
                            on_delete=models.PROTECT,
                            db_column='dataset_id'
                        )
    satellite         = models.ForeignKey(
                            Satellite,
                            on_delete=models.CASCADE,
                            db_column='satellite_id'
                        )
    timestamp         = models.DateTimeField()
    velocity          = models.DecimalField(max_digits=10, decimal_places=4)
    inclination       = models.DecimalField(max_digits=10, decimal_places=4)
    eccentricity      = models.DecimalField(max_digits=10, decimal_places=7)
    ra_of_asc_node    = models.DecimalField(max_digits=10, decimal_places=4)
    arg_of_pericenter = models.DecimalField(max_digits=10, decimal_places=4)
    mean_anomaly      = models.DecimalField(max_digits=10, decimal_places=4)
    mean_motion       = models.DecimalField(max_digits=12, decimal_places=8)
    bstar             = models.DecimalField(max_digits=12, decimal_places=8)
    altitude          = models.DecimalField(max_digits=10, decimal_places=4)
    latitude          = models.DecimalField(max_digits=9,  decimal_places=6)
    longitude         = models.DecimalField(max_digits=9,  decimal_places=6)

    class Meta:
        managed         = False
        db_table        = 'trajectory'
        unique_together = [['dataset', 'satellite', 'timestamp']]

    def __str__(self):
        return f"{self.satellite.name} @ {self.timestamp}"


class EarthScience(models.Model):
    satellite         = models.ForeignKey(
                            Satellite,
                            on_delete=models.CASCADE,
                            db_column='satellite_id'
                        )
    timestamp         = models.DateTimeField()
    land_surface_temp = models.DecimalField(max_digits=8, decimal_places=4)
    emissivity        = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    quality_flag      = models.CharField(max_length=10, null=True, blank=True)
    instrument        = models.CharField(max_length=50)
    lst_unit          = models.CharField(max_length=10, default='Kelvin')

    class Meta:
        managed         = False
        db_table        = 'earth_science'
        unique_together = [['satellite', 'timestamp']]

    def __str__(self):
        return f"{self.satellite.name} LST @ {self.timestamp}"


class OceanicScience(models.Model):
    satellite   = models.ForeignKey(
                      Satellite,
                      on_delete=models.CASCADE,
                      db_column='satellite_id'
                  )
    timestamp   = models.DateTimeField()
    sst         = models.DecimalField(max_digits=8, decimal_places=4)
    sst_anomaly = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    instrument  = models.CharField(max_length=50)
    sst_unit    = models.CharField(max_length=10, default='Celsius')

    class Meta:
        managed         = False
        db_table        = 'oceanic_science'
        unique_together = [['satellite', 'timestamp']]

    def __str__(self):
        return f"{self.satellite.name} SST @ {self.timestamp}"


class Research(models.Model):
    satellite        = models.OneToOneField(
                           Satellite,
                           on_delete=models.CASCADE,
                           primary_key=True,
                           db_column='satellite_id'
                       )
    research_field   = models.CharField(max_length=100)
    instrument       = models.CharField(max_length=100, null=True, blank=True)
    wavelength_band  = models.CharField(max_length=50, null=True, blank=True)
    data_archive_url = models.CharField(max_length=500, null=True, blank=True)
    mission_status   = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'research'

    def __str__(self):
        return f"{self.satellite.name} — {self.research_field}"


class Internet(models.Model):
    satellite      = models.OneToOneField(
                         Satellite,
                         on_delete=models.CASCADE,
                         primary_key=True,
                         db_column='satellite_id'
                     )
    coverage       = models.TextField(null=True, blank=True)
    frequency_band = models.CharField(max_length=20, null=True, blank=True)
    service_type   = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'internet'

    def __str__(self):
        return f"{self.satellite.name} — internet"


class Weather(models.Model):
    satellite        = models.OneToOneField(
                           Satellite,
                           on_delete=models.CASCADE,
                           primary_key=True,
                           db_column='satellite_id'
                       )
    coverage_region  = models.CharField(max_length=100)
    imaging_channels = models.IntegerField(null=True, blank=True)
    repeat_cycle_min = models.IntegerField(null=True, blank=True)
    instrument       = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'weather'

    def __str__(self):
        return f"{self.satellite.name} — weather"


class Navigation(models.Model):
    satellite     = models.OneToOneField(
                        Satellite,
                        on_delete=models.CASCADE,
                        primary_key=True,
                        db_column='satellite_id'
                    )
    constellation = models.CharField(max_length=50)
    signal_type   = models.CharField(max_length=50, null=True, blank=True)
    accuracy      = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'navigation'

    def __str__(self):
        return f"{self.satellite.name} — {self.constellation}"


class DeploysPayload(models.Model):
    vehicle          = models.ForeignKey(
                           LaunchVehicle,
                           on_delete=models.CASCADE,
                           db_column='vehicle_id'
                       )
    satellite        = models.ForeignKey(
                           Satellite,
                           on_delete=models.CASCADE,
                           db_column='satellite_id'
                       )
    deploy_date_time = models.DateTimeField()

    class Meta:
        managed         = False
        db_table        = 'deploys_payload'
        unique_together = [['vehicle', 'satellite']]

    def __str__(self):
        return f"{self.vehicle} deployed {self.satellite}"


class CommunicatesWith(models.Model):
    location  = models.ForeignKey(
                    CommunicationStation,
                    on_delete=models.CASCADE,
                    db_column='location',
                    to_field='location'
                )
    satellite = models.ForeignKey(
                    Satellite,
                    on_delete=models.CASCADE,
                    db_column='satellite_id'
                )

    class Meta:
        managed         = False
        db_table        = 'communicates_with'
        unique_together = [['location', 'satellite']]

    def __str__(self):
        return f"{self.satellite.name} ↔ {self.location}"