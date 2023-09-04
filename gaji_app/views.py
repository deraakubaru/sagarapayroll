from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status, permissions
from .models import Divisi, User, Karyawan, Gaji, Absen
from .serializers import DivisiSerializer, LoginSerializer, RegisterSerializer, UserSerializer, KaryawanSerializer, GajiSerializer, ExcellFileSerializer, AbsenSerializer, GajiListSerializer, GajiTetapUpdateSerializer, GajiFreelanceSerializer, GajiFreelanceCreateSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from datetime import datetime
from rest_framework.views import APIView
from django.db.models import Q
from .utils import absence_excel_file, user_excel_file, divisi_excel_file, riwayat_absen, hari_kerja, basic_salary, find_gaji_pokok, find_total_gaji
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


#DIVISI

class DivisiView(generics.ListAPIView):
    queryset = Divisi.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = DivisiSerializer
    
#USER

class LoginView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key,
                             "user_id": user.id,
                             "email": user.email,
                             "nama": user.nama}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email atau Password salah !"}, status=status.HTTP_401_UNAUTHORIZED)
        
    def login_view(request):
        return render(request, 'login.html')
    
    def dashboard_view(request):
        return render(request, 'base.html')
        
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()
        return Response({
            "user": RegisterSerializer(user, context=self.get_serializer_context()).data,
        })

class UserRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
class GajiFreelanceRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gaji.objects.all()
    serializer_class = GajiFreelanceCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        gaji_pokok = serializer.validated_data.get('gaji_pokok', instance.gaji_pokok)
        total_gaji = serializer.validated_data.get('total_gaji', instance.total_gaji)
        
        instance.gaji_pokok = gaji_pokok
        instance.total_gaji = total_gaji
        instance.save()
        return Response({
            "message": "Gaji Updated Successfully",
            "gaji_pokok": gaji_pokok,
            "total_gaji": total_gaji,
        })
    
class GajiRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gaji.objects.all()
    serializer_class = GajiTetapUpdateSerializer
    permission_classes = [permissions.AllowAny]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the existing Gaji instance
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        nip = instance.nip
        tunjangan_cuti = serializer.validated_data.get('tunjangan_cuti', instance.tunjangan_cuti)
        tunjangan_makan = serializer.validated_data.get('tunjangan_makan', instance.tunjangan_makan)
        tunjangan_transport = serializer.validated_data.get('tunjangan_transport', instance.tunjangan_transport)
        
        # Perform calculations or other necessary logic here
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        bulan = today.strftime("%B")
        total_hari_kerja = hari_kerja(current_year, current_month)
        hitung_absen = riwayat_absen(nip)
            
        
        jml_hari_masuk = 0
        for item in hitung_absen:
            if item['keterangan'] == 'masuk':
                jml_hari_masuk += item['count']
            
        karyawan = Karyawan.objects.get(nip=nip)
        posisi = karyawan.position
        divisi = karyawan.divisi
        upah_bulan = basic_salary(posisi, divisi)
        gaji_pokok = find_gaji_pokok(upah_bulan, total_hari_kerja, jml_hari_masuk)
        total_gaji = find_total_gaji(gaji_pokok, tunjangan_cuti, tunjangan_makan, tunjangan_transport)
            
        # Update the instance with new values
        instance.bulan = bulan
        instance.gaji_pokok = gaji_pokok
        instance.tunjangan_cuti = tunjangan_cuti
        instance.tunjangan_makan = tunjangan_makan
        instance.tunjangan_transport = tunjangan_transport
        instance.total_gaji = total_gaji
        instance.save()

        return Response({
            "message": "Gaji updated successfully",
            "bulan": bulan,
            "gaji_pokok": gaji_pokok,
            "tunjangan_cuti": instance.tunjangan_cuti,
            "tunjangan_transport": instance.tunjangan_transport,
            "tunjangan_makan": instance.tunjangan_makan,
            "hari": jml_hari_masuk,
            "total_gaji": total_gaji,
        })
      
class UpdateProfileView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Karyawan.objects.all()
    serializer_class = KaryawanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        
        karyawan = Karyawan.objects.get(user_id=user_id)
        return karyawan
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user

        divisi_id = request.data.get('divisi')
        if divisi_id:
            try:
                divisi = Divisi.objects.get(pk=divisi_id)
            except Divisi.DoesNotExist:
                return Response({"detail": "Invalid divisi ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            instance.divisi = divisi
            instance.save()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.nama = request.data.get('nama', user.nama)
        user.save()

        return super().update(request, *args, **kwargs)

class KaryawanTetapList(generics.ListAPIView):
    queryset = Karyawan.objects.filter(jenis_karyawan="tetap")
    permission_classes = [permissions.AllowAny]
    serializer_class = KaryawanSerializer
    
class KaryawanFreelanceList(generics.ListAPIView):
    queryset = Karyawan.objects.filter(jenis_karyawan="freelance")
    permission_classes = [permissions.AllowAny]
    serializer_class = KaryawanSerializer
    
class GajiFreelanceList(generics.ListAPIView):
    queryset = Gaji.objects.filter(nip__jenis_karyawan="freelance")
    permission_classes = [permissions.AllowAny]
    serializer_class = GajiFreelanceSerializer

class GajiFreelanceCreateView(generics.CreateAPIView):
    queryset = Gaji.objects.all()
    serializer_class = GajiFreelanceCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)
        nip = serializer.validated_data['nip']
        gaji_pokok = serializer.validated_data['gaji_pokok']
        total_gaji = serializer.validated_data['total_gaji']
        karyawan = Karyawan.objects.get(nip=nip)
        Gaji.objects.create(
            nip=karyawan,
            gaji_pokok=gaji_pokok,
            total_gaji=total_gaji,
        )
        return Response({
            'message': 'Data gaji berhasil ditambahkan',
            'gaji_pokok': gaji_pokok,
            'total_gaji': total_gaji,
        })
        
class GajiTetapList(generics.ListAPIView):
    queryset = Gaji.objects.filter(nip__jenis_karyawan="tetap")
    permission_classes = [permissions.AllowAny]
    serializer_class = GajiListSerializer

class GajiView(generics.CreateAPIView):
    serializer_class = GajiSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        nip = self.kwargs['nip']
        nama = self.kwargs['nama']
        
        condition = Q(user_id=user_id) | Q(nip = nip) | Q(nama=nama)
        
        karyawan = Karyawan.objects.get(condition)
        return karyawan
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)
        
        nip = serializer.validated_data['nip']
        
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        bulan = today.strftime("%B")
        total_hari_kerja = hari_kerja(current_year, current_month)
        hitung_absen = riwayat_absen(nip)
        
        jml_hari_masuk = 0
        jml_hari_cuti = 0
        
        for item in hitung_absen:
            if item['keterangan'] == 'masuk':
                jml_hari_masuk += item['count']
        
        for item in hitung_absen:
            if item['keterangan'] == 'cuti':
                jml_hari_cuti += item['count']
                
        if jml_hari_cuti > 5 :
            tunjangan_cuti = 500000
        else :
            tunjangan_cuti = 100000 * jml_hari_cuti
        
                
        karyawan = Karyawan.objects.get(nip=nip)
        posisi = karyawan.position
        divisi = karyawan.divisi
        upah_bulan = basic_salary(posisi, divisi)
        gaji_pokok = find_gaji_pokok(upah_bulan, total_hari_kerja, jml_hari_masuk)
        
        tunjangan_transport = upah_bulan * 0.10
        tunjangan_makan = upah_bulan * 0.10
        
        total_gaji = find_total_gaji(gaji_pokok, tunjangan_cuti, tunjangan_makan, tunjangan_transport)
        
        Gaji.objects.create(
            nip=karyawan,
            bulan=bulan,
            gaji_pokok=gaji_pokok,
            tunjangan_makan=tunjangan_makan,
            tunjangan_transport=tunjangan_transport,
            tunjangan_cuti=tunjangan_cuti,
            jml_hari_kerja=jml_hari_masuk,
            total_gaji=total_gaji,
        )     
            
        return Response({
            "message": "Gaji instance created successfully",
            "bulan": bulan,
            "gaji_pokok": gaji_pokok,
            "tunjangan_cuti": tunjangan_cuti,
            "tunjangan_transport": tunjangan_transport,
            "tunjangan_makan": tunjangan_makan,
            "hari": jml_hari_masuk,
            "total_gaji": total_gaji,
        })
       
class AbsencelImportView(APIView):
    def post(self, request, format=None):
        serializer = ExcellFileSerializer(data=request.data)
        if serializer.is_valid():
            excel_file = serializer.validated_data['file']
            success_count, error_messages = absence_excel_file(excel_file)
            response_data = {
                'success_count': success_count,
                'error_messages': error_messages
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDataImportView(APIView):
    def post(self, request, format=None):
        serializer = ExcellFileSerializer(data=request.data)
        if serializer.is_valid():
            excel_file = serializer.validated_data['file']
            success_count, error_messages = user_excel_file(excel_file)
            response_data = {
                'success_count': success_count,
                'error_messages': error_messages
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DivisiDataImportView(APIView):
    def post(self, request, format=None):
        serializer = ExcellFileSerializer(data=request.data)
        if serializer.is_valid():
            excel_file = serializer.validated_data['file']
            success_count, error_messages = divisi_excel_file(excel_file)
            response_data = {
                'success_count': success_count,
                'error_messages': error_messages
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AbsenView(generics.CreateAPIView):
    queryset = Absen.objects.all()
    serializer_class = AbsenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        absen = serializer.save()
        return Response({
            "absen": serializer.data, 
        })

class LogoutAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        # Token.objects.filter(user=request.user).delete()
        return Response({
            "message": "Logged out successfully"
        })
