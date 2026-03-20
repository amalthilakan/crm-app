from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .models import Customer
from .forms import CustomerForm, UserForm, UserUpdateForm

import pandas as pd
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from django.core.paginator import Paginator

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('customer_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile_update')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'crmapp/profile_update.html', {'form': form})


@login_required
def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'crmapp/user_list.html', {'users': users})


@login_required
def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'crmapp/user_detail.html', {'user_obj': user_obj})


@login_required
def user_create(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'User created successfully')
        return redirect('user_list')
    return render(request, 'crmapp/user_form.html', {'form': form, 'title': 'Create User'})


@login_required
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user_obj)

    if form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully')
        return redirect('user_list')

    return render(request, 'crmapp/user_form.html', {'form': form, 'title': 'Edit User'})


@login_required
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if user_obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')

    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('user_list')

    return render(request, 'crmapp/user_confirm_delete.html', {'user_obj': user_obj})


@login_required
def customer_list(request):
    qs = Customer.objects.all().order_by('-created_at')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)

    return render(request, 'crmapp/customer_list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'crmapp/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        messages.success(request, 'Customer created successfully')
        return redirect('customer_list')

    return render(request, 'crmapp/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, request.FILES or None, instance=customer)

    if form.is_valid():
        form.save()
        messages.success(request, 'Customer updated successfully')
        return redirect('customer_list')

    return render(request, 'crmapp/customer_form.html', {'form': form, 'title': 'Edit Customer'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully')
        return redirect('customer_list')

    return render(request, 'crmapp/customer_confirm_delete.html', {'customer': customer})


@login_required
def customer_bulk_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            messages.error(request, "No file uploaded.")
            return redirect('customer_bulk_upload')

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Only Excel files are allowed.")
            return redirect('customer_bulk_upload')

        try:
            df = pd.read_excel(excel_file, engine='openpyxl')

            df.columns = df.columns.astype(str).str.strip().str.lower()

            required = {'name', 'email', 'phone', 'address'}
            if not required.issubset(df.columns):
                messages.error(request, "Required columns: name, email, phone, address")
                return redirect('customer_bulk_upload')

            df = df.fillna('')
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

            df = df.drop_duplicates(subset=['email'])

            emails = df['email'].tolist()

            existing = {
                c.email: c for c in Customer.objects.filter(email__in=emails)
            }

            new_objs = []
            update_objs = []

            for _, row in df.iterrows():
                email = row['email']

                if not email:
                    continue

                try:
                    validate_email(email)
                except ValidationError:
                    continue

                if email in existing:
                    obj = existing[email]
                    obj.name = row['name']
                    obj.phone = row['phone']
                    obj.address = row['address']
                    update_objs.append(obj)
                else:
                    new_objs.append(Customer(
                        email=email,
                        name=row['name'],
                        phone=row['phone'],
                        address=row['address']
                    ))

            if new_objs:
                Customer.objects.bulk_create(new_objs)

            if update_objs:
                Customer.objects.bulk_update(update_objs, ['name', 'phone', 'address'])

            messages.success(
                request,
                f"Added {len(new_objs)} and updated {len(update_objs)} customers."
            )

            return redirect('customer_list')

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect('customer_bulk_upload')

    return render(request, 'crmapp/customer_bulk_upload.html')


@login_required
def customer_download_pdf(request):
    customers = Customer.objects.only('id', 'name', 'email', 'phone', 'created_at')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Customer Data Report", styles['Title']))
    elements.append(Spacer(1, 20))

    data = [['ID', 'Name', 'Email', 'Phone', 'Created']]

    for c in customers:
        data.append([
            str(c.id),
            c.name,
            c.email,
            c.phone,
            c.created_at.strftime("%b %d, %Y")
        ])

    table = Table(data, colWidths=[40, 120, 160, 100, 90])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4e73df")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#dddfeb")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fc")])
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="customers_report.pdf"'

    return response