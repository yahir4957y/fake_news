import io
import csv
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from app.infrastructure.repositories.reporte_repositorio import ReportesRepositorio

class ReporteService:
    """Servicio para generar reportes en PDF y CSV"""

    def __init__(self):
        # NUEVO: Inicializa el repositorio y ruta temporal de archivos
        self.repo = ReportesRepositorio()
        self.ruta_reportes = os.path.join(os.getcwd(), "reportes_temp")
        os.makedirs(self.ruta_reportes, exist_ok=True)

    def generar_reporte(self, usuario_id: str, verificacion_id: str, formato: str) -> dict:
        """NUEVO: Genera el reporte solicitado en PDF o CSV"""
        if formato not in ['pdf', 'csv']:
            raise ValueError(f"Formato no soportado: {formato}")

        datos = self.repo.obtener_detalle_analisis(verificacion_id, usuario_id)
        if not datos:
            raise ValueError("Análisis no encontrado o sin permisos")

        if formato == 'pdf':
            return self._generar_pdf(datos)
        else:
            return self._generar_csv(datos)

    def _parsear_resumen(self, resumen_raw) -> dict:
        if not resumen_raw:
            return {}
        try:
            return json.loads(resumen_raw)
        except (json.JSONDecodeError, TypeError):
            return {"detalles": str(resumen_raw)}

    def _generar_pdf(self, datos: dict) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_nombre = f"reporte_analisis_{datos['contenido_tipo']}_{timestamp}.pdf"
        archivo_path = os.path.join(self.ruta_reportes, archivo_nombre)

        resumen = self._parsear_resumen(datos.get('resumen'))
        detalles = resumen.get('detalles') or datos.get('resumen', 'Sin resumen disponible')
        veredicto_corto = resumen.get('veredicto_corto', '')
        analisis_contenido = resumen.get('analisis_contenido', '')
        indicadores = resumen.get('indicadores', [])
        contexto_factual = resumen.get('contexto_factual', '')
        tecnicas = resumen.get('tecnicas_manipulacion', [])
        nivel_riesgo = resumen.get('nivel_riesgo', '')
        score = float(datos.get('score_credibilidad') or 0)

        try:
            doc = SimpleDocTemplate(
                archivo_path,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            story = []
            styles = getSampleStyleSheet()

            titulo_style = ParagraphStyle(
                'titulo', parent=styles['Heading1'],
                fontSize=22, textColor=colors.HexColor('#1e293b'),
                spaceAfter=6, alignment=1
            )
            heading_style = ParagraphStyle(
                'heading', parent=styles['Heading2'],
                fontSize=12, textColor=colors.HexColor('#0f172a'),
                spaceAfter=6, spaceBefore=10
            )
            label_style = ParagraphStyle(
                'label', parent=styles['Normal'],
                fontSize=9, textColor=colors.HexColor('#64748b'),
                spaceAfter=3
            )

            story.append(Paragraph("REPORTE DE VERIFICACIÓN DE CONTENIDO", titulo_style))
            story.append(Paragraph("Generado por FakeNewsAI · Modelo: Gemini 2.5 Flash", label_style))
            story.append(Spacer(1, 0.2*inch))

            info = (
                f"<b>Usuario:</b> {datos['nombre_usuario'] or 'Anónimo'} &nbsp;|&nbsp; "
                f"<b>Email:</b> {datos['email_usuario']} &nbsp;|&nbsp; "
                f"<b>Fecha:</b> {datos['fecha_fin'].strftime('%d/%m/%Y %H:%M') if datos['fecha_fin'] else 'N/A'} &nbsp;|&nbsp; "
                f"<b>Tipo:</b> {datos['contenido_tipo'].upper()}"
            )
            story.append(Paragraph(info, styles['Normal']))
            story.append(Spacer(1, 0.25*inch))

            resultado_color = colors.HexColor('#22c55e') if 'verificado' in datos['estado'] else colors.HexColor('#ef4444')
            resultado_text = 'CONTENIDO REAL' if 'verificado' in datos['estado'] else 'DESINFORMACIÓN DETECTADA'

            tabla_resultado = Table([
                ['VEREDICTO', 'SCORE DE CREDIBILIDAD', 'NIVEL DE RIESGO'],
                [
                    Paragraph(f"<font color='white'><b>{resultado_text}</b></font>", styles['Normal']),
                    Paragraph(f"<font color='white'><b>{score:.0f} / 100</b></font>", styles['Normal']),
                    Paragraph(f"<font color='white'><b>{nivel_riesgo or datos.get('nivel_credibilidad') or 'N/A'}</b></font>", styles['Normal'])
                ]
            ], colWidths=[2.8*inch, 2*inch, 2*inch])
            tabla_resultado.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('BACKGROUND', (0, 1), (-1, 1), resultado_color),
                ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, 1), 13),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ]))
            story.append(tabla_resultado)
            story.append(Spacer(1, 0.2*inch))

            if veredicto_corto:
                story.append(Paragraph(f"<i>{veredicto_corto}</i>", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

            story.append(Paragraph("CONTENIDO ANALIZADO", heading_style))
            contenido_preview = datos['contenido_texto'] or datos['contenido_url'] or 'Contenido multimedia'
            contenido_preview = str(contenido_preview)[:600] + ('...' if len(str(contenido_preview)) > 600 else '')
            story.append(Paragraph(contenido_preview, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

            if analisis_contenido:
                story.append(Paragraph("QUÉ AFIRMA EL CONTENIDO", heading_style))
                story.append(Paragraph(analisis_contenido, styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

            if indicadores:
                story.append(Paragraph("INDICADORES DETECTADOS", heading_style))
                for ind in indicadores:
                    tipo = ind.get('tipo', 'neutro')
                    icono = '✓' if tipo == 'positivo' else ('✗' if tipo == 'negativo' else '·')
                    color_texto = '#22c55e' if tipo == 'positivo' else ('#ef4444' if tipo == 'negativo' else '#94a3b8')
                    story.append(Paragraph(
                        f"<font color='{color_texto}'><b>{icono}</b></font> {ind.get('descripcion', '')}",
                        styles['Normal']
                    ))
                story.append(Spacer(1, 0.15*inch))

            if contexto_factual:
                story.append(Paragraph("CONTEXTO FACTUAL", heading_style))
                story.append(Paragraph(contexto_factual, styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

            if tecnicas:
                story.append(Paragraph("TÉCNICAS DE MANIPULACIÓN DETECTADAS", heading_style))
                for t in tecnicas:
                    story.append(Paragraph(f"⚠ {t}", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

            story.append(Paragraph("ANÁLISIS COMPLETO", heading_style))
            story.append(Paragraph(detalles, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

            if datos.get('recomendacion'):
                story.append(Paragraph("RECOMENDACIÓN", heading_style))
                story.append(Paragraph(datos['recomendacion'], styles['Normal']))
                story.append(Spacer(1, 0.15*inch))

            if datos.get('fuentes_sugeridas'):
                story.append(Paragraph("FUENTES PARA VERIFICACIÓN", heading_style))
                fuentes = datos['fuentes_sugeridas']
                if isinstance(fuentes, list):
                    for fuente in fuentes[:5]:
                        nombre = fuente.get('nombre', fuente) if isinstance(fuente, dict) else str(fuente)
                        url = fuente.get('url', '') if isinstance(fuente, dict) else ''
                        texto = f"{nombre}" + (f" — {url}" if url else "")
                        story.append(Paragraph(f"• {texto}", styles['Normal']))

            story.append(Spacer(1, 0.25*inch))
            story.append(Paragraph(
                f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')} · Modelo: {datos.get('modelo_ia', 'gemini-2.5-flash')}</i>",
                styles['Normal']
            ))
            doc.build(story)

            return {'archivo_path': archivo_path, 'archivo_nombre': archivo_nombre, 'formato': 'pdf'}

        except Exception as e:
            raise Exception(f"Error generando PDF: {str(e)}")

    def _generar_csv(self, datos: dict) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_nombre = f"reporte_analisis_{datos['contenido_tipo']}_{timestamp}.csv"
        archivo_path = os.path.join(self.ruta_reportes, archivo_nombre)

        resumen = self._parsear_resumen(datos.get('resumen'))
        detalles = resumen.get('detalles') or datos.get('resumen', 'Sin resumen')
        veredicto_corto = resumen.get('veredicto_corto', '')
        analisis_contenido = resumen.get('analisis_contenido', '')
        indicadores = resumen.get('indicadores', [])
        contexto_factual = resumen.get('contexto_factual', '')
        tecnicas = resumen.get('tecnicas_manipulacion', [])
        nivel_riesgo = resumen.get('nivel_riesgo', '')
        score = float(datos.get('score_credibilidad') or 0)

        try:
            filas = [
                ['REPORTE DE VERIFICACIÓN DE CONTENIDO - FakeNewsAI', ''],
                ['', ''],
                ['INFORMACIÓN GENERAL', ''],
                ['Usuario', datos['nombre_usuario'] or 'Anónimo'],
                ['Email', datos['email_usuario']],
                ['Fecha de análisis', datos['fecha_fin'].strftime('%d/%m/%Y %H:%M') if datos['fecha_fin'] else 'N/A'],
                ['Tipo de contenido', datos['contenido_tipo'].upper()],
                ['', ''],
                ['RESULTADO', ''],
                ['Veredicto', 'CONTENIDO REAL' if 'verificado' in datos['estado'] else 'DESINFORMACIÓN DETECTADA'],
                ['Score de credibilidad', f"{score:.0f} / 100"],
                ['Nivel de riesgo', nivel_riesgo or datos.get('nivel_credibilidad') or 'N/A'],
                ['Veredicto corto', veredicto_corto],
                ['', ''],
                ['CONTENIDO ANALIZADO', ''],
                ['Preview', (datos['contenido_texto'] or datos['contenido_url'] or 'Multimedia')[:300]],
            ]

            if analisis_contenido:
                filas += [['', ''], ['QUÉ AFIRMA EL CONTENIDO', ''], ['Descripción', analisis_contenido]]

            if indicadores:
                filas += [['', ''], ['INDICADORES DETECTADOS', '']]
                for ind in indicadores:
                    tipo = ind.get('tipo', '').upper()
                    filas.append([tipo, ind.get('descripcion', '')])

            if contexto_factual:
                filas += [['', ''], ['CONTEXTO FACTUAL', ''], ['Contexto', contexto_factual]]

            if tecnicas:
                filas += [['', ''], ['TÉCNICAS DE MANIPULACIÓN', '']]
                for t in tecnicas:
                    filas.append(['Técnica detectada', t])

            filas += [
                ['', ''],
                ['ANÁLISIS COMPLETO', ''],
                ['Análisis', detalles],
                ['', ''],
                ['RECOMENDACIÓN', ''],
                ['Recomendación', datos.get('recomendacion', 'N/A')],
            ]

            if datos.get('fuentes_sugeridas') and isinstance(datos['fuentes_sugeridas'], list):
                filas += [['', ''], ['FUENTES PARA VERIFICACIÓN', '']]
                for i, fuente in enumerate(datos['fuentes_sugeridas'][:5], 1):
                    if isinstance(fuente, dict):
                        filas.append([f'Fuente {i}', fuente.get('nombre', '')])
                        filas.append([f'URL {i}', fuente.get('url', '')])
                    else:
                        filas.append([f'Fuente {i}', str(fuente)])

            filas += [
                ['', ''],
                ['METADATA', ''],
                ['Modelo IA', datos.get('modelo_ia', 'gemini-2.5-flash')],
                ['Generado en', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ]

            with open(archivo_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                writer.writerows(filas)

            return {'archivo_path': archivo_path, 'archivo_nombre': archivo_nombre, 'formato': 'csv'}

        except Exception as e:
            raise Exception(f"Error generando CSV: {str(e)}")
