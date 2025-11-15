"""Task to generate signed PDF contracts using WeasyPrint."""
from celery import shared_task
from django.template.loader import render_to_string
from io import BytesIO


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_contract_pdf_task(contract_id: int):
    """Generate a signed PDF for a contract and save it."""
    try:
        from contracts.models import Contract
        from django.core.files.base import ContentFile
        
        contract = Contract.objects.get(pk=contract_id)
        
        # Render HTML template for contract
        html_string = render_to_string('contracts/contract_pdf.html', {
            'contract': contract,
            'listing': contract.listing,
            'buyer': contract.buyer,
            'farmer': contract.listing.farmer,
            'signed_at': contract.signed_at,
        })
        
        # Generate PDF using WeasyPrint
        try:
            import weasyprint
            html = weasyprint.HTML(string=html_string)
            pdf_bytes = html.write_pdf()
        except ImportError:
            # Fallback: use xhtml2pdf if WeasyPrint not available
            from xhtml2pdf import pisa
            pdf_file = BytesIO()
            pisa.pisaDocument(BytesIO(html_string.encode('utf-8')), pdf_file)
            pdf_bytes = pdf_file.getvalue()
        
        filename = f'contract_{contract_id}_{contract.signed_at.timestamp()}.pdf'
        contract.contract_document.save(filename, ContentFile(pdf_bytes))
        contract.save()
        
        return f'PDF generated for contract {contract_id}'
    except Contract.DoesNotExist:
        return f'Contract {contract_id} not found'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)
