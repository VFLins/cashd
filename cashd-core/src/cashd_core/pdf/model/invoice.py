from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from cashd_core import data
from cashd_core.pdf.model.base import DocumentMeta


def InvoiceMeta(name) -> DocumentMeta:
    size = (72*mm, 220*mm)
    margin = (0, 1*mm, 0, 0)
    return DocumentMeta(size=size, margin=margin, name=name)


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
    C_HEADING = ParagraphStyle("c_para", parent=L_HEADING, alignment=1)
    C_PARA = ParagraphStyle("c_para", parent=L_PARA, alignment=1)
    C_BOLD = ParagraphStyle("c_bold", parent=L_BOLD, alignment=1)


class _Document:
    style = StyleSheet()
    buffer = []

    def __init__(self):
        self.meta = InvoiceMeta(name="test")
        self.doc = SimpleDocTemplate(
            str(self.meta.document_path),
            pagesize=self.meta.size,
            topMargin=self.meta.margin[0],
            rightMargin=self.meta.margin[1],
            bottomMargin=self.meta.margin[2],
            leftMargin=self.meta.margin[3],
        )
        self._write_header()
        self._write_content()
        self._write_footer()

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
        self.buffer.append(Paragraph(f"Data de Emissão: {now}", s.R_PARA))
        self.buffer.append(Spacer(1, 6 * mm))

    def _write_content(self):
        s = self.style

    def _write_footer(self):
        s = self.style
        self.buffer.append(Spacer(1, 6 * mm))
        self.buffer.append(Paragraph((". " * 22) + ".", s.C_PARA))
        self.buffer.append(Paragraph("Obrigado pela preferência!", s.C_PARA))

    def render(self):
        self.doc.build(self.buffer)
        print(f"PDF gerado com sucesso: {self.meta.document_path}")


class CustomerTransactions(_Document):
    def __init__(self, customer_id: int):
        self.customer = data.tbl_clientes()
        self.customer.read(row_id=customer_id)
        super().__init__()

    def _write_content(self):
        s = self.style
        transactions = list(self.customer.Transacs)[:10]
        content_width = self.meta.size[0] - self.meta.margin[1] - self.meta.margin[3]
        col_widths = [content_width * 0.50, content_width * 0.5]
        table_style = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])

        # table header
        table_head = Table(
            [
                [
                    Paragraph("<b>Data</b>", s.L_BOLD),
                    Paragraph("<b>Valor (R$)</b>", s.R_BOLD),
                ]
            ],
            colWidths=col_widths,
        )

        transactions = [
            [Paragraph(tr["data"].strftime("%d/%m/%Y"), s.L_PARA), Paragraph(tr["valor"], s.R_PARA)]
            for tr in transactions
        ]

        table_body = Table(transactions, colWidths=col_widths)

        col_totais = [content_width * 0.6, content_width * 0.4]
        dados_totais = [
            [Paragraph("<b>QTD. TOTAL DE ITENS</b>", s.L_BOLD), Paragraph("4", s.R_BOLD)],
            [Paragraph("<b>VALOR TOTAL R$</b>", s.L_BOLD), Paragraph("<b>51,50</b>", s.R_BOLD)],
            [Paragraph("FORMA DE PAGAMENTO: Cartão Débito", s.L_PARA), Paragraph("51,50", s.R_PARA)],
        ]

        tabela_totais = Table(dados_totais, colWidths=col_widths)
        tabela_totais.setStyle(table_style)
        self.buffer.append(Paragraph(f"Últimas {len(transactions)} transações de", s.L_PARA))
        self.buffer.append(Paragraph(f"{self.customer.Id}, {self.customer.NomeCompleto}", s.L_BOLD))
        self.buffer.append(Spacer(1, 2 * mm))
        self.buffer.append(table_head)
        self.buffer.append(table_body)
        self.buffer.append(Spacer(1, 2 * mm))
        self.buffer.append(Paragraph("Saldo no momento de emissão", s.C_PARA))
        self.buffer.append(Paragraph(f"R$ {self.customer.Saldo}", s.C_HEADING))


if __name__ == "__main__":
    doc = CustomerTransactions(1)
    doc.render()
