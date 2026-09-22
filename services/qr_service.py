import qrcode
import io
import base64

class QRService:
    @staticmethod
    def generate_qr_base64(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        
        # Encode to base64 for embedding in HTML
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
