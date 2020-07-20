# -*- coding: utf-8 -*-
from typing import List
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from app.models.statistics import Statistics
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from reportlab.lib import colors


def create_statistic_pdf(statistics_info, global_filename):
    elements = []
    statistics_list: List[Statistics] = Statistics.get_statistics_by_ids(statistics_info)
    for statistics in statistics_list:
        data = get_pdf_statistics_data(statistics)
        table = Table(data, rowHeights=25, colWidths=[2.5 * inch, 2.5 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch])
        set_style_for_statistics_table(table, data)
        elements.append(table)
        # add one line free space
        elements.append(Paragraph('<font size=0>tinkering</font>', getSampleStyleSheet()['Normal']))
    pdf = SimpleDocTemplate(
        title='Statystyki',
        filename=global_filename,
        pagesize=letter
    )
    pdf.build(elements)


def set_style_for_statistics_table(table, data):
    for i in range(0, len(data)):
        if i == 0:
            bc = colors.khaki
        else:
            bc = colors.white
        table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bc)]
            )
        )
    table.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEABOVE', (0, 2), (0, 2), 2, colors.black),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]
    ))


def get_pdf_statistics_data(statistics: Statistics):
    data = [[statistics.user_index, statistics.course_name, statistics.user_points,
             statistics.course_points, (str(statistics.get_percent_value()) + '%')]]
    for user_exercise in statistics.user_exercises:
        data.append(
            [user_exercise.exercise.lesson.name, user_exercise.exercise.name, user_exercise.points,
             user_exercise.max_points, (str(user_exercise.get_percent_value()) + '%')])
    return data


def create_solutions_pdf(solutions, global_filename):
    data, elements = [], []
    for solution in solutions:
        data.append([solution.author.index, solution.get_course().name, solution.get_lesson().name,
                     solution.exercise.name, solution.send_date, solution.points, solution.status])
    table = Table(data, rowHeights=25,
                  colWidths=[0.7 * inch, 1 * inch, 1.5 * inch, 1.5 * inch, 2 * inch, 0.4 * inch, 1.2 * inch])
    table.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEABOVE', (0, 2), (0, 2), 2, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ]
    ))
    elements.append(table)
    pdf = SimpleDocTemplate(
        title='Rozwiązania',
        filename=global_filename,
        pagesize=letter
    )
    pdf.build(elements)
