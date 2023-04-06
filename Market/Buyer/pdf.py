from borb.pdf import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from datetime import datetime
import random
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import HexColor, X11Color
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell
from Market.User.routes import current_user


class InvoicePdfGenerator:
    def __init__(self, buyer, user, date_from, date_to, total_product_money, perivous_money_history):
        self.buyer = buyer
        self.user = user
        self.date_from = date_from
        self.date_to = date_to
        self.total_product_money = total_product_money
        self.perivous_money_history = perivous_money_history
    #
    # Helvetica - Bold


    @staticmethod
    def _build_invoice_information(self):
        table_001 = Table(number_of_rows=7, number_of_columns=2)
        table_001.add(Paragraph("اسم المشتري : "))
        table_001.add(Paragraph(f"{self.buyer.name}"))

        table_001.add(Paragraph(f"تاريخ و وقت استخراج الفاتورة : ", horizontal_alignment=Alignment.RIGHT))
        table_001.add(Paragraph(f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}", horizontal_alignment=Alignment.RIGHT))

        table_001.add(Paragraph("رقم التليفون"))
        table_001.add(Paragraph(f"{self.buyer.phone_num}"))

        table_001.add(Paragraph("اسم مستخرج الفاتورة : "))
        table_001.add(Paragraph(f"{current_user.name}"))

        table_001.add(Paragraph(f"من تاريخ : ", horizontal_alignment=Alignment.RIGHT))
        table_001.add(Paragraph(f"{self.date_from}", horizontal_alignment=Alignment.RIGHT))

        table_001.add(Paragraph("اسم منشيء المشتري : "))
        table_001.add(Paragraph(f"{self.user.name}"))

        table_001.add(Paragraph(f"الي تاريخ : ", horizontal_alignment=Alignment.RIGHT))
        table_001.add(Paragraph(f"{self.date_to}", horizontal_alignment=Alignment.RIGHT))

        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        return table_001

    @staticmethod
    def make_items_of_products_table(self,page_layout):
        table_001 = Table(number_of_rows= len(self.buyer.goods) + 2, number_of_columns=8)
        for h in ["المنتج", "السعر", "الكمیة", "اجمالي المعاملة", "المدفوع", "الباقي", "تاریخ المعاملة", "ملاحظات"]:
            table_001.add(
                TableCell(
                    Paragraph(h, font_color=X11Color("White")),
                    background_color=HexColor("000000"),
                )
            )
        odd_color = HexColor("BBBBBB")
        even_color = HexColor("FFFFFF")

        # enumerate([("Product 1", 2, 50), ("Product 2", 4, 60), ("Labor", 14, 60)])
        row_number = 1
        for product in self.buyer.goods:
            c = even_color if row_number % 2 == 0 else odd_color
            table_001.add(TableCell(Paragraph(product.name), background_color=c))
            table_001.add(TableCell(Paragraph("ج " + str(product.price)), background_color=c))
            table_001.add(TableCell(Paragraph(str(product.quantity)), background_color=c))
            table_001.add(TableCell(Paragraph("ج " + str(product.quantity * product.price)), background_color=c))
            table_001.add(TableCell(Paragraph("ج " + str(product.pay_quantity)), background_color=c))
            table_001.add(TableCell(Paragraph("ج " + str( (product.quantity * product.price) - product.pay_quantity) ), background_color=c))
            table_001.add(TableCell(Paragraph(str(product.date)), background_color=c))
            table_001.add(TableCell(Paragraph("مبيعات"), background_color=c))
            row_number += 1
            # Optionally add some empty rows to have a fixed number of rows for styling purposes

        for i in range(8):
            table_001.add(TableCell(Paragraph(" "), background_color= even_color))

        table_001.add(TableCell(Paragraph("الاجمالي : ", horizontal_alignment=Alignment.RIGHT, ), col_span=3, ))
        table_001.add(TableCell(Paragraph(f"{self.total_product_money}", horizontal_alignment=Alignment.RIGHT)))
        table_001.add(TableCell(Paragraph("ما قبله : ", horizontal_alignment=Alignment.RIGHT, ),
                                col_span=3, ))
        table_001.add(TableCell(Paragraph(f"{self.perivous_money_history}", horizontal_alignment=Alignment.RIGHT)))
        table_001.add(
            TableCell(Paragraph("اخر تحصيل : ", horizontal_alignment=Alignment.RIGHT), col_span=3, ))
        table_001.add(TableCell(Paragraph(f"{self.buyer.last_collection_money}", horizontal_alignment=Alignment.RIGHT)))

        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        print(table_001)
        return table_001


    # @staticmethod
    # def _build_billing_and_shipping_information(self):
    #     table_001 = Table(number_of_rows=6, number_of_columns=2)
    #     table_001.add(
    #         Paragraph(
    #             "BILL TO",
    #             background_color=HexColor("263238"),
    #             font_color=X11Color("White"),
    #         )
    #     )
    #     table_001.add(
    #         Paragraph(
    #             "SHIP TO",
    #             background_color=HexColor("263238"),
    #             font_color=X11Color("White"),
    #         )
    #     )
    #     table_001.add(Paragraph("[Recipient Name]"))  # BILLING
    #     table_001.add(Paragraph("[Recipient Name]"))  # SHIPPING
    #     table_001.add(Paragraph("[Company Name]"))  # BILLING
    #     table_001.add(Paragraph("[Company Name]"))  # SHIPPING
    #     table_001.add(Paragraph("[Street Address]"))  # BILLING
    #     table_001.add(Paragraph("[Street Address]"))  # SHIPPING
    #     table_001.add(Paragraph("[City, State, ZIP Code]"))  # BILLING
    #     table_001.add(Paragraph("[City, State, ZIP Code]"))  # SHIPPING
    #     table_001.add(Paragraph("[Phone]"))  # BILLING
    #     table_001.add(Paragraph("[Phone]"))  # SHIPPING
    #     table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    #     table_001.no_borders()
    #     return table_001

    def get_pdf_created(self):

        # Create document
        pdf = Document()

        # Add page
        page = Page()

        pdf.insert_page(page, -1)

        page_layout = SingleColumnLayout(page)
        page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)


        # Invoice information table
        page_layout.add(self._build_invoice_information(self))

        # Empty paragraph for spacing
        page_layout.add(Paragraph(" "))

        # Itemized description
        page_layout.add(self.make_items_of_products_table(self,page_layout))

        with open("output2.pdf", "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)


