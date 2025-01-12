# This helper script loads the list of localization files and
# exposes the current localization file name and path to the javascript side

import os
import gradio as gr
from pathlib import Path
from modules import script_callbacks, shared
from modules.paths import extensions_dir
import json

localizations = {}

localizations_dirs = [shared.cmd_opts.localizations_dir if "localizations_dir" in shared.cmd_opts else "localizations"]
localizations_dirs += [os.path.join(extensions_dir, ext_name, "localizations") for ext_name in os.listdir(extensions_dir)]

def list_localizations(dirname):
    if not os.path.isdir(dirname):
        return

    print("dirname: ", dirname)

    for file in os.listdir(dirname):
        fn, ext = os.path.splitext(file)
        if ext.lower() != ".json":
            continue

        localizations[fn] = os.path.join(dirname, file)

    from modules import scripts
    for file in scripts.list_scripts("localizations", ".json"):
        fn, ext = os.path.splitext(file.filename)
        localizations[fn] = file.path

    print("localizations: ", localizations)

def list_all_localizations():
    for locale_dir in localizations_dirs:
        list_localizations(locale_dir)

list_all_localizations()

# Webui root path
ROOT_DIR = Path().absolute()

# The localization files
I18N_DIRS = { k: str(Path(v).relative_to(ROOT_DIR).as_posix()) for k, v in localizations.items() }
print(I18N_DIRS)
    
# Register extension options
def on_ui_settings():
    BL_SECTION = ("bl", "Bilingual Localization")
    # enable in settings
    shared.opts.add_option("bilingual_localization_enabled", shared.OptionInfo(True, "Enable Bilingual Localization", section=BL_SECTION))
    
    # enable devtools log
    shared.opts.add_option("bilingual_localization_logger", shared.OptionInfo(False, "Enable Devtools Log", section=BL_SECTION))

    # current localization file
    shared.opts.add_option("bilingual_localization_file", shared.OptionInfo("None", "Localization file (Please leave `User interface` - `Localization` as None)", gr.Dropdown, lambda: {"choices": ["None"] + list(localizations.keys())}, refresh=lambda: list_all_localizations(), section=BL_SECTION))

    # translation order
    shared.opts.add_option("bilingual_localization_order", shared.OptionInfo("Translation First", "Translation display order", gr.Radio, {"choices": ["Translation First", "Original First"]}, section=BL_SECTION))

    # all localization files path in hidden option
    shared.opts.add_option("bilingual_localization_dirs", shared.OptionInfo(json.dumps(I18N_DIRS), "Localization dirs", section=BL_SECTION, component_args={"visible": False}))

script_callbacks.on_ui_settings(on_ui_settings)
