from django.shortcuts import render, redirect
from .models import Configuracion
from .forms import ConfiguracionForm

def inicializar_configuracion(request):
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES)
        if form.is_valid():
            configuracion = form.save(commit=False)
            configuracion.id = 1
            configuracion.save()
            return redirect('index')
    else:
        form = ConfiguracionForm()
    
    return render(request, 'inicializar_configuracion.html', {'form': form})