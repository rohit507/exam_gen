from exam_gen.mixins.settings.map import *

class Foo(SettingsManager):

    settings.new_setting(
        "test",
        desc = "test setting",
        options = {
            "option_1": "bla bla",
            "option_2": """
            *Bla* **Bla** *Bla*


            !!! Error
                Oh no!
            """,
            }
        )

    settings.new_setting_group(
        name = "group",
        desc = """
        Here's some more compllex formatting in a group description.

        > Like a quote

        !!! Note
            And another admontition
        """,
        )

    settings.group.new_setting(
        "subgroup_setting",
        desc = "test desc",
        )
    settings.test = 3


    def func(self):
        """some test documentation"""
        pass

class Bar(Foo):
    """
    testing
    """

    settings.new_setting(
        "test2",
        long_desc = """
        Verbose test setting number 2 with **formatting**.

        | And | a | table |
        | :--: | :-- | --: |
        | foo | bar | buzz |
        | bing | bong | boop |
        """
        )
    settings.test2 = 2
    settings.test2 += settings.test
    settings.test = 4

class Buzz(Foo):
    settings.new_setting(
        "test3",
        desc = "test setting 3"
        )
    settings.test3 = "hello"
    settings.test3 += " " + str(settings.test)
    settings.test = 12
