from django.shortcuts import render, redirect
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.http import HttpResponse
from .models import Student, BusPass, BusRoute
from .forms import StudentForm, BusPassForm, BusRouteForm


@login_required
def home(request):
    query = request.GET.get("q")
    students_qs = Student.objects.all()

    if query:
        students_qs = students_qs.filter(
            models.Q(name__icontains=query) |
            models.Q(roll_number__icontains=query) |
            models.Q(email__icontains=query)
        )

    # 🔹 Pagination: 10 students per page
    paginator = Paginator(students_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "students": page_obj,   # iterable in template
        "page_obj": page_obj,   # for pagination controls
    }
    return render(request, 'transport/home.html', context)


@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = StudentForm()

    bus_routes = BusRoute.objects.all()
    return render(request, 'transport/add_student.html', {'form': form, 'bus_routes': bus_routes})


@login_required
def issue_bus_pass(request):
    if request.method == 'POST':
        form = BusPassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Bus pass issued successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = BusPassForm()

    students = Student.objects.all()
    return render(request, 'transport/issue_bus_pass.html', {'form': form, 'students': students})


@login_required
def bus_routes(request):
    routes = BusRoute.objects.all()
    return render(request, 'transport/bus_routes.html', {'routes': routes})


@login_required
def add_route(request):
    if request.method == 'POST':
        form = BusRouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Bus route added successfully.")
            return redirect('bus_routes')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = BusRouteForm()

    return render(request, 'transport/add_route.html', {'form': form})


@login_required
def download_bus_pass(request, student_id):
    student = Student.objects.get(id=student_id)
    bus_pass = student.bus_passes.first()
    route = student.bus_route

    # Prepare HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BusPass_{student.roll_number}.pdf"'

    # PDF canvas with A4 size
    width, height = A4
    c = canvas.Canvas(response, pagesize=A4)

    # ---------- HEADER ----------
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 40, "Maharishi Markandeshwar (Deemed to be University)")

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 65, "UNIVERSITY TRANSPORT BUS PASS")
    c.setFillColor(colors.black)

    # Optional top line
    c.setLineWidth(1)
    c.line(40, height - 80, width - 40, height - 80)

    # ---------- CARD / RECEIPT BOX ----------
    box_left = 40
    box_bottom = height - 320
    box_width = width - 80
    box_height = 220

    # Draw rounded rectangle
    c.setLineWidth(1)
    c.roundRect(box_left, box_bottom, box_width, box_height, 10, stroke=1, fill=0)

    # Inside padding
    x_label = box_left + 15
    x_value = box_left + 160
    y = box_bottom + box_height - 30
    line_gap = 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "Student Name:")
    c.setFont("Helvetica", 12)
    c.drawString(x_value, y, f"{student.name}")

    y -= line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "Roll Number:")
    c.setFont("Helvetica", 12)
    c.drawString(x_value, y, f"{student.roll_number}")

    y -= line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "Email:")
    c.setFont("Helvetica", 12)
    c.drawString(x_value, y, f"{student.email}")

    if route:
        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Route:")
        c.setFont("Helvetica", 12)
        c.drawString(
            x_value,
            y,
            f"{route.route_name} ({route.start_location} → {route.end_location})"
        )

        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Driver:")
        c.setFont("Helvetica", 12)
        driver_text = route.driver_name if route.driver_name else "Not Assigned"
        c.drawString(x_value, y, driver_text)

        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Capacity:")
        c.setFont("Helvetica", 12)
        c.drawString(x_value, y, str(route.capacity))

    # Divider inside card
    y -= line_gap
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    c.line(box_left + 10, y + 10, box_left + box_width - 10, y + 10)
    c.setDash(1, 0)  # reset dash

    # Bus pass details
    y -= line_gap
    if bus_pass:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Pass Number:")
        c.setFont("Helvetica", 12)
        c.drawString(x_value, y, bus_pass.pass_number)

        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Issue Date:")
        c.setFont("Helvetica", 12)
        c.drawString(x_value, y, str(bus_pass.issue_date))

        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Expiry Date:")
        c.setFont("Helvetica", 12)
        c.drawString(x_value, y, str(bus_pass.expiry_date))

        y -= line_gap
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Status:")
        c.setFont("Helvetica", 12)
        status_text = "Expired" if bus_pass.is_expired else "Active"
        status_color = colors.red if bus_pass.is_expired else colors.green
        c.setFillColor(status_color)
        c.drawString(x_value, y, status_text)
        c.setFillColor(colors.black)
    else:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y, "Pass Status:")
        c.setFont("Helvetica", 12)
        c.drawString(x_value, y, "No active bus pass found.")

    # ---------- FOOTER ----------
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawRightString(width - 40, box_bottom - 20, "This is a system generated bus pass receipt.")
    c.setFillColor(colors.black)

    c.showPage()
    c.save()
    return response

