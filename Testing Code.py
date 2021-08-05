from win10toast import ToastNotifier
toaster = ToastNotifier()
toaster.show_toast("Hello World!!!",
                   "Python is 10 seconds awsm!",
                   icon_path="Logo.ico",
                   duration=20)

print("success?")