#!/usr/bin/python3

'''

@author     Aan Kurniawan <aan.phpy@gmail.com>
@since      2023
'''
import os
import configparser
import getpass

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


BASE_PATH = os.path.join(os.path.dirname(__file__))
APP_INI = 'app.ini'
HOME_PATH = '/home/{}'.format(getpass.getuser())
DEFAULT_WINEPREFIX = HOME_PATH + '/.wine'
DEFAULT_WINE_EXEC = 'WINEARCH=win32 WINEPREFIX={} wine {}'


class AppConfig(object):

    ini_file = None
    config = None
    apps: list = []

    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.config = configparser.ConfigParser()
        self.parse()

    def parse(self):
        self.apps = []
        self.config.clear()
        self.config.read(self.ini_file)
        for section in self.config.sections():
            self.apps.append({
                'name': self.config.get(section, 'name'),
                'label': self.config.get(section, 'label'),
                'category': self.config.get(section, 'category'),
                'type': self.config.get(section, 'type'),
                'params': self.config.get(section, 'params'),
                'program': self.config.get(section, 'program'),
                'wineprefix': self.config.get(section, 'wineprefix')
            })

    def search(self, keyword, by='label'):
        if not self.apps:
            return []

        apps = []
        for app in self.apps:
            if app.get(by) == keyword:
                apps.append(app)

        return apps

    def search_by_name(self, keyword):
        app = self.search(keyword, 'name')
        return app[0] if app else None

    def search_by_label(self, keyword):
        return self.search(keyword, 'label')

    def search_by_category(self, keyword):
        return self.search(keyword, 'category')

    def search_by_type(self, keyword):
        return self.search(keyword, 'type')

    def search_by_wineprefix(self, keyword):
        return self.search(keyword, 'wineprefix')

    def write(self):
        new_data = ''
        for app in self.apps:
            new_data = '{}[{}]\n'.format(new_data, app.get('name'))
            new_data = '{}name={}\n'.format(new_data, app.get('name'))
            new_data = '{}label={}\n'.format(new_data, app.get('label'))
            new_data = '{}category={}\n'.format(new_data, app.get('category'))
            new_data = '{}type={}\n'.format(new_data, app.get('type'))
            new_data = '{}params={}\n'.format(new_data, app.get('params'))
            new_data = '{}program={}\n'.format(new_data, app.get('program'))
            new_data = '{}wineprefix={}\n'.format(new_data, app.get('wineprefix'))
            new_data = '{}\n'.format(new_data)

        if not self.apps:
            new_data = ''

        with open(self.ini_file, 'w') as f:
            f.write(new_data)
            f.close()

        return True


class AppListbox(ttk.Frame):

    parent_frame = None
    parent = None
    app_listbox = None

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent', None)
        if self.parent:
            del (kwargs['parent'])
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.app_listbox = tk.Listbox(self)
        scrollbar = ttk.Scrollbar(self)

        self.app_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.app_listbox.yview)

        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.app_listbox.bind('<Double-Button>', self.parent.app_run)
        self.app_listbox.bind('<KeyPress>', self.parent.app_update)

        self.populate()

    def populate(self):
        if not self.parent.app_config.apps:
            return None

        self.parent.app_config.apps = self.sort_by_name()

        wineprefixs = []
        categories = []
        types = []
        for app in self.parent.app_config.apps:
            wineprefix = app.get('wineprefix')
            category = app.get('category')
            app_type = app.get('type')
            if not wineprefix:
                wineprefix = DEFAULT_WINEPREFIX
            if wineprefix not in wineprefixs:
                wineprefixs.append(wineprefix)
            if category not in categories:
                categories.append(category)
            if app_type not in types:
                types.append(app_type)
            self.app_listbox.insert(tk.END, "{}".format(app.get('label')))
        self.parent.containers = wineprefixs
        self.parent.app_categories = categories
        self.parent.app_types = types

    def sort_by_name(self):
        app_lists = self.parent.app_config.apps
        app_labels = [app.get('label') for app in app_lists]
        app_labels.sort()
        apps = []
        for app_label in app_labels:
            app_index = 0
            for app in app_lists:
                if app_label == app.get('label'):
                    apps.append(app)
                app_index += 1
        return apps


class FormAbout(tk.Toplevel):

    parent = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paret = args[0] if args else None
        self.init()

    def init(self):
        self.init_ui()

    def init_ui(self):
        str_about = "================================================================================\n"
        str_about += "ZIA WINE LAUNCHER v0.1\n"
        str_about += "By Aan Kurniawan <aan.phpy@gmail.com> (L) 2023\n"
        str_about += "================================================================================\n"
        str_about += "- Just follow the menu and your intuition.\n"
        str_about += "- Right-click on the launcher list for an additional menu\n"
        str_about += "\tuse the shortcut listed there.\n"
        str_about += "- You can config windows version\n"
        str_about += "\t- From App > Containers\n"
        str_about += "\t- Choose the containers\n"
        str_about += "\t- Click Tools button\n"
        str_about += "\t- Click Config button\n"
        str_about += "- You can config container from this Tools window.\n"
        str_about += "- New features will continue to be added soon.\n"

        fmain = ttk.Frame(self, width=680, height=300)
        text_about = tk.Text(fmain, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(fmain)

        text_about.insert(tk.END, str_about)
        text_about.config(state=tk.DISABLED)

        scrollbar.config(command=text_about.yview)

        fmain.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fmain.pack_propagate(0)
        text_about.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)


class FormWineTools(tk.Toplevel):
    parent = None
    wineprefix = None

    def __init__(self, *args, **kwargs):
        if kwargs.get('parent', None):
            self.parent = kwargs['parent']
            del (kwargs['parent'])
        if kwargs.get('wineprefix', None):
            self.wineprefix = kwargs['wineprefix']
            del (kwargs['wineprefix'])
        if not self.wineprefix:
            self.wineprefix = DEFAULT_WINEPREFIX
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.title('Zia: Wine Tools')
        fmain = ttk.Frame(self, border=5)
        button_config = ttk.Button(fmain, text='Config', command=self.wine_config)
        button_regedit = ttk.Button(fmain, text='Regedit', command=self.wine_regedit)
        button_explorer = ttk.Button(fmain, text='Explorer', command=self.wine_explorer)
        button_cmd = ttk.Button(fmain, text='CMD', command=self.wine_cmd)
        button_close = ttk.Button(fmain, text='Close', command=self.destroy)

        fmain.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        button_config.pack(side=tk.TOP, fill=tk.X)
        button_regedit.pack(side=tk.TOP, fill=tk.X)
        button_explorer.pack(side=tk.TOP, fill=tk.X)
        button_cmd.pack(side=tk.TOP, fill=tk.X)
        button_close.pack(side=tk.TOP, fill=tk.X)

        self.grab_set()
        self.transient(self.parent)

    def wine_config(self):
        os.system(DEFAULT_WINE_EXEC.format(self.wineprefix, 'winecfg &'))

    def wine_regedit(self):
        os.system(DEFAULT_WINE_EXEC.format(self.wineprefix, 'regedit &'))

    def wine_explorer(self):
        os.system(DEFAULT_WINE_EXEC.format(self.wineprefix, 'explorer &'))

    def wine_cmd(self):
        terminal_path = '/usr/bin/gnome-terminal'
        wine_exec = DEFAULT_WINE_EXEC.format(self.wineprefix, 'cmd')
        str_cmd = "{} -e 'bash -c \"{}\"' ".format(terminal_path, wine_exec)
        os.system(str_cmd)


class WinePrefixDirForm(tk.Toplevel):
    parent = None
    root_path = None
    wineprefix_dir = None
    callback = None

    def __init__(self, *args, **kwargs):
        if kwargs.get('parent', None):
            self.parent = kwargs.get('parent', None)
            del (kwargs['parent'])
        if kwargs.get('root_path', None):
            self.root_path = kwargs.get('root_path', None)
            del (kwargs['root_path'])
        if kwargs.get('callback', None):
            self.callback = kwargs.get('callback', None)
            del (kwargs['callback'])
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        fapp = ttk.Frame(self, border=5, width=400, height=120)

        finput = ttk.Frame(fapp)
        label_wineprefix_dir = ttk.Label(finput, text='Wine Container Name e.g. mywine7')
        self.wineprefix_dir = ttk.Entry(finput)

        faction = ttk.Frame(fapp)
        button_save = ttk.Button(faction, text='OK', command=self.save)
        button_cancel = ttk.Button(faction, text='Cancel', command=self.destroy)

        fapp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fapp.pack_propagate(0)

        label_wineprefix_dir.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.wineprefix_dir.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        finput.pack(fill=tk.X, expand=True, pady=5)

        button_save.pack(side=tk.RIGHT)
        button_cancel.pack(side=tk.RIGHT)
        faction.pack(fill=tk.X, expand=True)

        self.grab_set()
        self.transient(self.parent)
        self.wineprefix_dir.focus()

    def save(self):
        if self.wineprefix_dir.get(): 
            root_path = self.root_path if self.root_path else HOME_PATH
            wineprefix = os.path.join(root_path, self.wineprefix_dir.get())
            drive_c = os.path.join(wineprefix, 'drive_c')
            if not os.path.exists(drive_c):
                os.system(DEFAULT_WINE_EXEC.format(wineprefix, 'winecfg'))
            if self.callback:
                self.callback(wineprefix)
            self.destroy()
        else:
            messagebox.showerror('Error', 'Wine container name required', parent=self)


class FormAddLauncher(tk.Toplevel):
    LABEL_WIDTH = 15
    ROW_GAP = 5
    parent = None
    wineprefix = None
    init_data = None

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent', None)
        if kwargs.get('parent', None):
            self.parent = kwargs['parent']
            del (kwargs['parent'])
        if kwargs.get('wineprefix', None):
            self.wineprefix = kwargs['wineprefix']
            del (kwargs['wineprefix'])
        else:
            self.wineprefix = DEFAULT_WINEPREFIX
        if kwargs.get('init_data', None):
            self.init_data = kwargs['init_data']
            del (kwargs['init_data'])
        super().__init__(*args, **kwargs)
        self.init()

    def init(self):
        self.init_ui()

    def init_ui(self):
        self.title('Zia: Add Launcher')

        row_name = ttk.Frame(self)
        label_name = ttk.Label(row_name, text='Name', width=self.LABEL_WIDTH, anchor='w')
        self.entry_name = ttk.Entry(row_name)

        row_label = ttk.Frame(self)
        label_label = ttk.Label(row_label, text='Label', width=self.LABEL_WIDTH, anchor='w')
        self.entry_label = ttk.Entry(row_label)

        row_category = ttk.Frame(self)
        label_category = ttk.Label(row_category, text='Category', width=self.LABEL_WIDTH, anchor='w')
        self.entry_category = ttk.Entry(row_category)

        row_type = ttk.Frame(self)
        label_type = ttk.Label(row_type, text='Type', width=self.LABEL_WIDTH, anchor='w')
        self.entry_type = ttk.Entry(row_type)

        row_program = ttk.Frame(self)
        label_program = ttk.Label(row_program, text='Program', width=self.LABEL_WIDTH, anchor='w')
        self.entry_program = ttk.Entry(row_program)
        button_browse = ttk.Button(row_program, text='Browse', command=self.browse_app)

        row_params = ttk.Frame(self)
        label_params = ttk.Label(row_params, text='Params', width=self.LABEL_WIDTH, anchor='w')
        self.entry_params = ttk.Entry(row_params)

        row_buttons = ttk.Frame(self)
        button_save = ttk.Button(row_buttons, text='Save', command=self.save)
        button_cancel = ttk.Button(row_buttons, text='Cancel', command=self.destroy)

        if self.init_data:
            self.entry_name.insert(0, self.init_data.get('name', None))
            self.entry_label.insert(0, self.init_data.get('label', None))
            self.entry_category.insert(0, self.init_data.get('category', None))
            self.entry_type.insert(0, self.init_data.get('type', None))
            self.entry_params.insert(0, self.init_data.get('params', None))
            self.entry_program.insert(0, self.init_data.get('program', None))

        row_name.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        label_name.pack(side=tk.LEFT)
        self.entry_name.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        row_label.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        label_label.pack(side=tk.LEFT)
        self.entry_label.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        row_category.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        self.entry_category.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        label_category.pack(side=tk.LEFT)

        row_type.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        label_type.pack(side=tk.LEFT)
        self.entry_type.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        row_program.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        label_program.pack(side=tk.LEFT)
        self.entry_program.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        button_browse.pack(side=tk.RIGHT)

        row_params.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        label_params.pack(side=tk.LEFT)
        self.entry_params.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        row_buttons.pack(side=tk.TOP, fill=tk.X, padx=self.ROW_GAP, pady=self.ROW_GAP)
        button_save.pack(side=tk.RIGHT)
        button_cancel.pack(side=tk.RIGHT)

        self.grab_set()
        self.transient(self.parent)
        self.focus()

    def save(self):
        launcher = {
            'category': self.entry_category.get() if self.entry_category.get() else 'Applications',
            'type': self.entry_type.get() if self.entry_type.get() else 'windows',
            'params': self.entry_params.get(),
            'wineprefix': self.wineprefix
        }

        has_error = False

        if not self.entry_name.get():
            has_error = True
            messagebox.showerror('Error', 'Name required', parent=self)
        else:
            launcher['name'] = self.entry_name.get()

        if not self.entry_label.get():
            has_error = True
            messagebox.showerror('Error', 'Label required', parent=self)
        else:
            launcher['label'] = self.entry_label.get()

        if not self.entry_program.get():
            has_error = True
            messagebox.showerror('Error', 'Program required', parent=self)
        else:
            launcher['program'] = self.entry_program.get()

        if not has_error:
            is_app_exists = False
            app_index = 0
            for app in self.parent.app_config.apps:
                if app.get('name') == launcher['name']:
                    is_app_exists = True
                    self.parent.app_config.apps[app_index] = launcher
                app_index += 1
            if not is_app_exists:
                self.parent.app_config.apps.append(launcher)
            self.parent.app_config.write()
            messagebox.showinfo('Success', 'Launcher saved', parent=self)
            self.parent.reload()
            self.destroy()

    def browse_app(self):
        initialdir = os.path.join(self.wineprefix, 'drive_c')
        fpath = filedialog.askopenfile(
            parent=self,
            initialdir=initialdir,
            filetypes=[('Windows Program', '.exe .lnk')])
        if fpath:
            file_path = ("{}".format(fpath.name)).replace(initialdir, 'C:').replace('/', '\\')
            self.entry_program.delete(0, tk.END)
            self.entry_program.insert(0, file_path)


class FormContainer(tk.Toplevel):

    STR_PATCH_BLANK_OPTION = 'No Containers. Click Add.' 
    parent = None
    app_config = None

    def __init__(self, *args, **kwargs):
        if kwargs.get('parent', None):
            self.parent = kwargs['parent']
            self.app_config = self.parent.app_config
            del (kwargs['parent'])
        if not self.parent.containers:
            self.parent.containers = [self.STR_PATCH_BLANK_OPTION]
        super().__init__(*args, **kwargs)
        self.init()

    def init(self):
        self.init_ui()

    def init_ui(self):
        self.title('Zia: Containers')

        fmain = ttk.Frame(self, border=5)
        fmain.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # fmain.pack_propagate(0)

        self.container = tk.StringVar(self)
        self.container.set(self.parent.containers[0])

        fcontainers = ttk.Frame(fmain)
        # self.dropdown_containers = tk.OptionMenu(fcontainers, self.container, *self.parent.containers)
        self.dropdown_containers = ttk.Combobox(fcontainers, textvariable=self.container, state='readonly')
        self.dropdown_containers['values'] = self.parent.containers
        button_add = ttk.Button(fcontainers, text='Add', command=self.add_container)
        button_run_explorer = ttk.Button(fcontainers, text='Run EXE/Installer', command=self.run_explorer)
        button_add_launcher = ttk.Button(fcontainers, text='Add Launcher', command=self.add_launcher)
        button_tools = ttk.Button(fcontainers, text='Tools', command=self.run_tools)
        button_close = ttk.Button(fcontainers, text='Close', command=self.destroy)

        self.dropdown_containers.pack(side=tk.TOP, fill=tk.X)
        button_add.pack(side=tk.TOP, fill=tk.X)
        button_run_explorer.pack(side=tk.TOP, fill=tk.X)
        button_add_launcher.pack(side=tk.TOP, fill=tk.X)
        button_tools.pack(side=tk.TOP, fill=tk.X)
        button_close.pack(side=tk.TOP, fill=tk.X)
        fcontainers.pack(side=tk.TOP, fill=tk.X, expand=True, padx=2)

        self.grab_set()
        self.transient(self.parent)

    def add_container(self):
        initialdir = HOME_PATH
        fpath = filedialog.askdirectory(
            parent=self, 
            initialdir=initialdir)
        if fpath:
            WinePrefixDirForm(parent=self, root_path=fpath, callback=self.append_container)

    def run_explorer(self):
        if self.container.get() == self.STR_PATCH_BLANK_OPTION:
            messagebox.showerror('Error', 'Click \'Add\' to add container', parent=self)
        else:
            wineprefix = self.dropdown_containers.get()
            os.system(DEFAULT_WINE_EXEC.format(wineprefix, 'explorer'))

    def append_container(self, wineprefix):
        if not wineprefix:
            return None
        if self.STR_PATCH_BLANK_OPTION in self.parent.containers:
            index = self.parent.containers.index(self.STR_PATCH_BLANK_OPTION)
            del (self.parent.containers[index])
        if wineprefix not in self.parent.containers:
            self.parent.containers.append(wineprefix)
            self.dropdown_containers['values'] = self.parent.containers
            # self.dropdown_containers['menu'].add_command(
            #     label=wineprefix,
            #     command=tk._setit(self.container, wineprefix))
            # self.container.set(wineprefix)
            self.dropdown_containers.current(len(self.parent.containers) - 1)

    def add_launcher(self):
        if self.STR_PATCH_BLANK_OPTION in self.parent.containers:
            messagebox.showerror('Error', "Click 'Add' to add container.", parent=self)
        else:
            # FormAddLauncher(parent=self, wineprefix=self.container.get())
            FormAddLauncher(parent=self, wineprefix=self.dropdown_containers.get())

    def run_tools(self):
        if self.STR_PATCH_BLANK_OPTION in self.parent.containers:
            messagebox.showerror('Error', "Click 'Add' to add container.", parent=self)
        else:
            FormWineTools(parent=self, wineprefix=self.dropdown_containers.get())

    def reload(self):
        self.parent.reload()


class ZiaApp(tk.Tk):

    KEY_ESC = 9
    KEY_E = 26
    KEY_C = 54
    KEY_D = 40
    KEY_DELETE = 119

    app_config = None
    containers: list = []
    app_categories: list = []
    app_types: list = []

    def __init__(self, app_config: AppConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_config = app_config
        self.init()

    def init(self):
        self.init_ui()
        self.init_menu()

    def init_ui(self):
        self.title('Zia Wine Launcher v0.1')

        fmain = ttk.Frame(self, width=600, height=300)
        fmain.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fmain.pack_propagate(0)

        self.listbox_apps = AppListbox(fmain, parent=self)
        self.listbox_apps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def init_menu(self):
        menubar = tk.Menu(self)

        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(label='Containers', command=self.manage_containers)
        app_menu.add_separator()
        app_menu.add_command(label='Reload', command=self.reload)
        app_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='App', menu=app_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self.about)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.config(menu=menubar)

        #Context Menu
        self.context_menu = tk.Menu(self.listbox_apps, tearoff=False)
        self.context_menu.add_command(label='Edit [e]', command=self.edit_launcher)
        self.context_menu.add_command(label='Config [c]', command=self.config_launcher)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='Delete [d]', command=self.delete_launcher)

        self.listbox_apps.app_listbox.bind('<Button-3>', self.show_context_menu)
        self.listbox_apps.app_listbox.bind('<Button-1>', self.hide_context_menu)

    def show_context_menu(self, e):
        self.context_menu.post(e.x_root, e.y_root)

    def hide_context_menu(self, e):
        self.context_menu.unpost()

    def about(self):
        about = FormAbout(self)
        about.focus()

    def app_run(self, e):
        program = None
        if self.listbox_apps.app_listbox.curselection():
            program = self.app_config.apps[self.listbox_apps.app_listbox.curselection()[0]]
        if not program:
            messagebox.showerror('Error', 'Please select a program.', parent=self)
        else:
            exec_cmd = DEFAULT_WINE_EXEC.format(
                program.get('wineprefix'),
                '"{}" {} &'.format(
                    program.get('program'),
                    program.get('params')))
            print('=====> RUN APP: ', exec_cmd)
            os.system(exec_cmd)

    def app_update(self, e):
        if e.keycode == self.KEY_D or e.keycode == self.KEY_DELETE:
            self.delete_launcher()
        elif e.keycode == self.KEY_E:
            self.edit_launcher()
        elif e.keycode == self.KEY_C:
            self.config_launcher()
        elif e.keycode == self.KEY_ESC:
            self.hide_context_menu(e)

    def delete_launcher(self):
        if self.listbox_apps.app_listbox.curselection():
            program_index = self.listbox_apps.app_listbox.curselection()[0]
            program = self.app_config.apps[program_index]
            deleted = messagebox.askokcancel('Warning', 'Delete this {}?'.format(program.get('label')), parent=self)
            if deleted:
                del (self.app_config.apps[program_index])
                self.app_config.write()
                self.reload()
        else:
            messagebox.showerror('Error', 'Please select a launcher', parent=self)

    def edit_launcher(self):
        if self.listbox_apps.app_listbox.curselection():
            program_index = self.listbox_apps.app_listbox.curselection()[0]
            program = self.app_config.apps[program_index]
            FormAddLauncher(parent=self, wineprefix=program.get('wineprefix'), init_data=program)
        else:
            messagebox.showerror('Error', 'Please select a launcher', parent=self)

    def config_launcher(self):
        if self.listbox_apps.app_listbox.curselection():
            program_index = self.listbox_apps.app_listbox.curselection()[0]
            program = self.app_config.apps[program_index]
            FormWineTools(parent=self, wineprefix=program.get('wineprefix'))
        else:
            messagebox.showerror('Error', 'Please select a launcher', parent=self)

    def manage_containers(self):
        form_container = FormContainer(parent=self)
        form_container.focus()

    def reload(self):
        self.listbox_apps.app_listbox.delete(0, tk.END)
        self.app_config.parse()
        # for app in self.app_config.apps:
        #     self.listbox_apps.app_listbox.insert(tk.END, "{}".format(app.get('label')))
        self.listbox_apps.populate()

    def not_implemented(self, parent=None):
        messagebox.showinfo('Zia: Info', 'Feature not yet implemented', parent=parent if parent else self)


def run_app():
    '''
    Run App
    '''
    app = ZiaApp(AppConfig(os.path.join(BASE_PATH, APP_INI)))
    style = ttk.Style()
    active_style = 'aqua' if 'aqua' in style.theme_names() else style.theme_names()[0]
    style.theme_use(active_style)
    app.mainloop()


if __name__ == '__main__':
    run_app()
