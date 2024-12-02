import logging

from behave.runner import ModelRunner

import features
from features import environment_desktop

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
logging.getLogger("faker").setLevel(logging.ERROR)
logging.getLogger("WDM").setLevel(logging.ERROR)


def extend_behave_hooks():
    """
    Extend Behave hooks with custom hooks code.
    """
    behave_run_hook = ModelRunner.run_hook
    # noinspection PyUnresolvedReferences
    behavex_env = features.environment_desktop
    print("Executing against DESKTOP browsers...\n")

    def run_hook(self, name, context, *args):
        if name == "before_all":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.before_all(context)
        elif name == "before_feature":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.before_feature(context, *args)
        elif name == "before_scenario":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.before_scenario(context, *args)
        elif name == "after_step":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.after_step(context, *args)
        elif name == "after_scenario":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.after_scenario(context, *args)
        elif name == "after_feature":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.after_feature(context, *args)
        elif name == "after_all":
            behave_run_hook(self, name, context, *args)
            # noinspection PyUnresolvedReferences
            behavex_env.after_all(context)
        else:
            behave_run_hook(self, name, context, *args)

    ModelRunner.run_hook = run_hook


extend_behave_hooks()
