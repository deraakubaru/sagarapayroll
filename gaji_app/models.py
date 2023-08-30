from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
import datetime
import uuid

ABSENSI = (
    ("masuk", "Masuk"),
    ("sakit", "Sakit"),
    ("izin", "Izin"),
    ("cuti", "Cuti"),
)

KARYAWAN_TYPE_CHOICES = (
    ("tetap", "Karyawan Tetap"),
    ("freelance", "Freelancer"),
    ("outsourcing", "Karyawan Outsourcing"),
)

KARYAWAN_POSITION_CHOICES = (
    ("direksi", "Direksi"),
    ("manajer", "Manajer"),
    ("staff", "Karyawan Outsourcing"),  
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    created_at = models.DateField(default=datetime.date.today)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class Divisi(models.Model):
    nama_divisi = models.CharField(max_length=200, blank=True, default="")
    def __str__(self):
        return self.nama_divisi
    
class Karyawan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=15, blank=True, unique=True, null=True)
    nama = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=50, blank=True, default="")
    phone_number = models.CharField(max_length=25, blank=True, default="")
    position = models.CharField(max_length=40, choices=KARYAWAN_POSITION_CHOICES)
    divisi = models.ForeignKey(Divisi, on_delete=models.CASCADE, default=None, null=True, blank=True)
    jenis_karyawan = models.CharField(max_length=40, choices=KARYAWAN_TYPE_CHOICES)
    def __str__(self):
        return self.nip
    
class Gaji(models.Model):
    gaji_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nip = models.ForeignKey(Karyawan, on_delete=models.CASCADE, to_field='nip')
    bulan = models.CharField(max_length=20, choices=[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], null=True)
    jml_hari_kerja = models.IntegerField(default=0)
    gaji_pokok = models.IntegerField(null=True)
    tunjangan_sakit = models.IntegerField(null=True)
    tunjangan_cuti = models.IntegerField(null=True)
    tunjangan_makan = models.IntegerField(null=True)
    tunjangan_transport = models.IntegerField(null=True)
    total_gaji = models.IntegerField(null=True)
    
class Absen(models.Model):
    absen_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tanggal = models.DateField(null=True)
    nip = models.ForeignKey(Karyawan, on_delete=models.CASCADE, to_field='nip')
    keterangan = models.CharField(max_length=20, choices=ABSENSI)