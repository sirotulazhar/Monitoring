class RoleHandler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, role, feature):
        if self.next_handler:
            return self.next_handler.handle(role, feature)
        return False  # Default: deny access

class SuperAdminHandler(RoleHandler):
    def handle(self, role, feature):
        if role == "superadmin":
            return True  # Superadmin bisa akses semua fitur
        return super().handle(role, feature)

class AdminHandler(RoleHandler):
    def handle(self, role, feature):
        if role == "admin":
            restricted_features = ["Detail Harian Transaksi"]  # Gunakan nama menu yang benar
            return feature not in restricted_features  # Admin tidak bisa akses fitur ini
        return super().handle(role, feature)

class UserHandler(RoleHandler):
    def handle(self, role, feature):
        if role == "user":
            allowed_features = ["Dashboard"]  # User hanya bisa akses Dashboard
            return feature in allowed_features
        return super().handle(role, feature)

# Urutan pengecekan: SuperAdmin -> Admin -> User
handler = SuperAdminHandler(AdminHandler(UserHandler()))
