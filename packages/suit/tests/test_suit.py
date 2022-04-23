import pathlib

from suit.suit_config import SuitConfig, ProjectConfig
from suit.scripts.specs import ShellScriptSpec
from suit.targets import TargetConfig, TargetConfigData


def test_targets_sorted_relatively_to_root():
    target_config = TargetConfig(pathlib.Path("root/packages/package-a"), TargetConfigData())
    suit_config = SuitConfig(pathlib.Path("root/"), ProjectConfig(), [target_config])
    assert suit_config.targets == {"packages/package-a": target_config}


def test_templates():
    suit_config = SuitConfig(
        pathlib.Path("root/"),
        ProjectConfig.parse_obj(
            {
                "templates": {
                    "package": {
                        "scripts": {
                            "black": "black"
                        }
                    },
                }
            }
        ),
        [],
    )

    template_scripts = suit_config.project_config.templates["package"].scripts
    assert isinstance(template_scripts["black"], ShellScriptSpec)
