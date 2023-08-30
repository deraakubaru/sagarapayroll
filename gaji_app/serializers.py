from .models import Gaji, Absen, User, Karyawan, Divisi
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class GajiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gaji
        fields = ['tunjangan_sakit', 'tunjangan_cuti', 'tunjangan_makan', 'tunjangan_transport', 'nip']

class GajiFreelanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gaji
        fields = ['gaji_id', 'nip', 'total_gaji', 'gaji_pokok']
        
class GajiFreelanceSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='nip.nama')
    nama_divisi = serializers.CharField(source='nip.divisi.nama_divisi')
    class Meta:
        model = Gaji
        fields = ['gaji_id', 'nip', 'nama', 'total_gaji', 'gaji_pokok', 'nama_divisi']
        
class GajiListSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='nip.nama')
    class Meta:
        model = Gaji
        fields = ['gaji_id', 'nip', 'nama', 'gaji_pokok', "tunjangan_sakit", "tunjangan_cuti", "tunjangan_makan", 'tunjangan_transport', 'total_gaji']

class GajiTetapUpdateSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='nip.nama')
    class Meta:
        model = Gaji
        fields = ["nip", "nama", "gaji_id", "tunjangan_sakit", "tunjangan_cuti", "tunjangan_makan", 'tunjangan_transport']

class ExcellFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class AbsenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absen
        fields = '__all__'
        
    def create(self, validated_data):
        tanggal = validated_data['tanggal']
        keterangan = validated_data['keterangan']
        nip = validated_data['nip']
        karyawan = Karyawan.objects.get(nip=nip)
        return Absen.objects.create(
            nip=karyawan,
            tanggal=tanggal,
            keterangan=keterangan,
        )
        
class DivisiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divisi
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nama', 'is_active', 'is_staff', 'created_at']
        
class KaryawanSerializer(serializers.ModelSerializer):
    user_nama = serializers.CharField(source='user.nama', read_only=True)
    class Meta:
        model = Karyawan
        fields = ['nip', 'nama', 'address', 'phone_number', 'position', 'divisi', 'jenis_karyawan', 'user_nama']
        
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True, write_only = True)
    class Meta:
        model = User
        fields = ('email', 'password')
        
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required= True, validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Email already used'
            )
        ],
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    nama = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password','password2', 'nama')
        
    def validate(self, attrs):
            
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            email = validated_data['email'],
            nama = validated_data['nama'],
        )
        user.is_active = True
        user.set_password(validated_data['password'])
        user.save()
        Karyawan.objects.create(
                user=user,
                nama=validated_data['nama'],
                )
        return user
        
        