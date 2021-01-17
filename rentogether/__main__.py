from rentogether.app import MainApplication
import tkinter

def main():
    root = tkinter.Tk()
    root.title('RenTogether')
    app = MainApplication(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()