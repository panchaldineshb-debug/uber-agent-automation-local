import subprocess

class MacNotifier:
    @staticmethod
    def notify_admin(title, message):
        """Sends a native macOS notification that mirrors to Apple Watch."""
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(["osascript", "-e", script])

# Usage
# MacNotifier.notify_admin("SarabiLabs", "Son's Uber has been booked successfully!")
