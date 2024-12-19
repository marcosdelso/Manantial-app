import qrcode

# Reemplaza esto con tu IP local y puerto
server_url = "http://10.2.0.2:8000/"  # Cambia 192.168.x.x por tu IP local

# Genera el código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(server_url)
qr.make(fit=True)

# Crea la imagen del QR
img = qr.make_image(fill_color="black", back_color="white")
img.save("server_qr.png")
print("QR generado y guardado como 'server_qr.png'")
