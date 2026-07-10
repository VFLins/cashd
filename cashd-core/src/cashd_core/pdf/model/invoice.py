from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from datetime import datetime
from pathlib import Path


class StyleSheet:
    styles = getSampleStyleSheet()
    L_HEADING = ParagraphStyle(
        "l_heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=11,
    )
    L_PARA = ParagraphStyle(
        "l_para",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=9,
    )
    L_BOLD = ParagraphStyle(
        "l_bold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=9,
    )
    R_PARA = ParagraphStyle("r_para", parent=L_PARA, alignment=2)
    R_BOLD = ParagraphStyle("r_bold", parent=L_BOLD, alignment=2)
    C_PARA = ParagraphStyle("c_para", parent=L_PARA, alignment=1)
    C_BOLD = ParagraphStyle("c_bold", parent=L_BOLD, alignment=1)


class _Document:
    style = StyleSheet()
    buffer = []

    def __init__(self):
        self.doc = SimpleDocTemplate(
            str(self.file_path),
            pagesize=(self.w, self.h),
            topMargin=self.t_margin,
            rightMargin=self.r_margin,
            bottomMargin=self.b_margin,
            leftMargin=self.l_margin,
        )
        self._write_header()
        self._write_content()
        self._write_footer()

    @property
    def w(self) -> float:
        """Width of canvas where content can be printed."""
        return 72*mm

    @property
    def h(self) -> float:
        """Height of canvas where content can be printed."""
        return 220*mm

    @property
    def t_margin(self) -> float:
        """Top margin inside the canvas."""
        return 3*mm

    @property
    def r_margin(self) -> float:
        """Right margin inside the canvas."""
        return 0*mm

    @property
    def b_margin(self) -> float:
        """Bottom margin inside the canvas."""
        return 0*mm

    @property
    def l_margin(self) -> float:
        """Left margin inside the canvas."""
        return 0*mm

    @property
    def file_path(self) -> Path:
        return Path("file.pdf")

    def _write_header(self):
        s = self.style
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Cashd
        self.buffer.append(Paragraph("<b>CASHD</b>", s.L_HEADING))
        self.buffer.append(Spacer(1, 1 * mm))
        self.buffer.append(Paragraph("Controle de recebíveis à ver", s.L_PARA))
        self.buffer.append(Spacer(1, 4 * mm))
        # Store info
        self.buffer.append(Paragraph("<b>NOME DA EMPRESA</b>", s.L_PARA))
        self.buffer.append(Paragraph("CNPJ: 12.345.678/0001-99", s.L_PARA))
        self.buffer.append(Paragraph("Av. Paulista, 1000 - São Paulo/SP", s.L_PARA))
        # Timestamp
        self.buffer.append(Spacer(1, 6 * mm))
        self.buffer.append(Paragraph(f"Data de Emissão: {now}", s.C_PARA))
        self.buffer.append(Spacer(1, 6 * mm))

    def _write_content(self):
        s = self.style
        self.buffer.append(Paragraph("Conteúdo aqui", s.L_PARA))

    def _write_footer(self):
        s = self.style
        self.buffer.append(Spacer(1, 6 * mm))
        self.buffer.append(Paragraph((". " * 22) + ".", s.C_PARA))
        self.buffer.append(Paragraph("Obrigado pela preferência!", s.C_PARA))

    def render(self):
        self.doc.build(self.buffer)
        print(f"PDF gerado com sucesso: {self.file_path}")


class CustomerTransactions(_Document):
    def __init__(self, customer_id: int):
        super().__init__()

    def _write_content(self):
        s = self.style
        content_width = self.w - (self.l_margin * 2)

        self.buffer.append(Paragraph("<b>CÓD | DESC | QTD | UN | VL UN | VL TOT</b>", s.C_BOLD))
        self.buffer.append(Paragraph("-" * 50, s.L_PARA))

        col_widths = [content_width * 0.50, content_width * 0.15, content_width * 0.35]
        dados_produtos = [
            # Colunas: [Descrição, Qtd x Un, Valor Total]
            [Paragraph("001 REFRIGERANTE LATA 350ML", s.L_PARA), Paragraph("1 UN x 5,00", s.L_PARA), Paragraph("5,00", s.R_PARA)],
            [Paragraph("002 PASTEL DE CARNE ESPECIAL", s.L_PARA), Paragraph("2 UN x 12,00", s.L_PARA), Paragraph("24,00", s.R_PARA)],
            [Paragraph("003 BATATA FRITA COMPLETA", s.L_PARA), Paragraph("1 UN x 22,50", s.L_PARA), Paragraph("22,50", s.R_PARA)],
        ]

        tabela_produtos = Table(dados_produtos, colWidths=col_widths)
        tabela_produtos.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        self.buffer.append(tabela_produtos)
        self.buffer.append(Paragraph("-" * 50, s.L_PARA))

        col_totais = [content_width * 0.6, content_width * 0.4]
        dados_totais = [
            [Paragraph("<b>QTD. TOTAL DE ITENS</b>", s.L_BOLD), Paragraph("4", s.R_BOLD)],
            [Paragraph("<b>VALOR TOTAL R$</b>", s.L_BOLD), Paragraph("<b>51,50</b>", s.R_BOLD)],
            [Paragraph("FORMA DE PAGAMENTO: Cartão Débito", s.L_PARA), Paragraph("51,50", s.R_PARA)],
        ]

        tabela_totais = Table(dados_totais, colWidths=col_totais)
        tabela_totais.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        self.buffer.append(tabela_totais)
        self.buffer.append(Paragraph("-" * 50, s.L_PARA))


if __name__ == "__main__":
    doc = CustomerTransactions(1)
    doc.render()
