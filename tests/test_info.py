"""
__author__ = "Patrick Renner"
__copyright__ = "Copyright 2020, Pomfort GmbH"

__license__ = "MIT"
__maintainer__ = "Patrick Renner, Alexander Sahm"
__email__ = "opensource@pomfort.com"
"""

import os
import shutil

from click.testing import CliRunner
from freezegun import freeze_time

import ascmhl.commands


@freeze_time("2020-01-16 09:15:00")
def test_simple_info_fails_no_history(fs, simple_mhl_history):
    runner = CliRunner()
    os.rename("/root/ascmhl", "/root/_ascmhl")
    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/Stuff.txt"])
    assert result.exit_code == 30


@freeze_time("2020-01-16 09:15:00")
def test_simple_info(fs, simple_mhl_history):
    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/Stuff.txt"])
    assert (
        result.output
        == "Info with history at path: /root\nStuff.txt:\n  Generation 1 (2020-01-15T13:00:00+00:00) xxh64:"
        " 94c399c2a9a21f9a (original)\n"
    )
    assert result.exit_code == 0


@freeze_time("2020-01-16 09:15:00")
def test_verbose_sf_info(fs):
    fs.create_file("/root/A/A1.txt", contents="A1\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64"])
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64"])
    os.rename("/root/A/A1.txt", "/root/A/_A1.txt")
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-dr"])

    result = runner.invoke(ascmhl.commands.create, ["/root/A"])
    os.rename("/root/A/_A1.txt", "/root/A/__A1.txt")
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-dr"])

    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/A/__A1.txt", "-v"])
    assert (
        result.output
        == """Info with history at path: /root/A
A1.txt:
  Generation 1 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
  Generation 2 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (verified) 
    /root/A/A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
Info with history at path: /root/A
_A1.txt:
  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/_A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
  Generation 4 (2020-01-16T09:15:00+00:00) xxh128: f50890cfaaec8a14d8a611f11484ec72 (verified) xxh64: 95e230e90be29dd6 (verified) 
    /root/A/_A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
Info with history at path: /root/A
__A1.txt:
  Generation 5 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/__A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
"""
    )
    assert result.exit_code == 0


@freeze_time("2020-01-16 09:15:00")
def test_info(fs, simple_mhl_history):
    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "xxh64"])
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "md5"])
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "xxh64"])
    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/Stuff.txt"])
    assert (
        result.output == "Info with history at path: /root\nStuff.txt:\n"
        "  Generation 1 (2020-01-15T13:00:00+00:00) xxh64: 94c399c2a9a21f9a (original)\n"
        "  Generation 2 (2020-01-16T09:15:00+00:00) xxh64: 94c399c2a9a21f9a (verified)\n"
        "  Generation 3 (2020-01-16T09:15:00+00:00) md5: 9eb84090956c484e32cb6c08455a667b (verified) xxh64: 94c399c2a9a21f9a (verified)\n"
        "  Generation 4 (2020-01-16T09:15:00+00:00) xxh64: 94c399c2a9a21f9a (verified)\n"
    )
    assert result.exit_code == 0


@freeze_time("2020-01-16 09:15:00")
def test_altered_file(fs, simple_mhl_history):
    # alter a file
    with open("/root/Stuff.txt", "a") as file:
        file.write("!!")
    CliRunner().invoke(ascmhl.commands.create, ["/root"])
    CliRunner().invoke(ascmhl.commands.create, ["/root", "-h", "md5"])

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/Stuff.txt"])
    assert (
        result.output
        == "Info with history at path: /root\nStuff.txt:\n  Generation 1 (2020-01-15T13:00:00+00:00) xxh64:"
        " 94c399c2a9a21f9a (original)\n  Generation 2 (2020-01-16T09:15:00+00:00) xxh64: 2346e97eb08788cc (failed)\n"
        "  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 2346e97eb08788cc (failed)\n"
    )
    assert result.exit_code == 0


@freeze_time("2020-01-16 09:15:00")
def test_nested_info(fs, nested_mhl_histories):
    CliRunner().invoke(ascmhl.commands.create, ["/root", "-h", "xxh64"])
    CliRunner().invoke(ascmhl.commands.create, ["/root", "-h", "md5"])

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/Stuff.txt"])
    assert (
        result.output == "Info with history at path: /root\nStuff.txt:\n"
        "  Generation 1 (2020-01-15T13:00:00+00:00) xxh64: 94c399c2a9a21f9a (original)\n"
        "  Generation 2 (2020-01-16T09:15:00+00:00) xxh64: 94c399c2a9a21f9a (verified)\n"
        "  Generation 3 (2020-01-16T09:15:00+00:00) md5: 9eb84090956c484e32cb6c08455a667b (verified) xxh64: 94c399c2a9a21f9a (verified)\n"
    )
    assert result.exit_code == 0


@freeze_time("2020-01-16 09:15:00")
def test_diff_info_renamed_file(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/AA/AA1.txt", contents="AA1\n")
    fs.create_file("/root/A/AA/ignore.txt", contents="AA1\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-i", "ignore.txt"])
    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "md5", "-i", "ignore.txt"])
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "xxh64", "-i", "ignore.txt"])
    os.rename("/root/A/A1.txt", "/root/A/_A1.txt")
    os.rename("/root/A/AA/AA1.txt", "/root/A/AA/_AA1.txt")
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-dr"])
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "xxh64"])
    os.rename("/root/A/AA/_AA1.txt", "/root/A/AA/__AA1.txt")
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-dr"])

    os.remove("/root/A/AA/__AA1.txt")
    fs.create_file("/root/_B/B3.txt", contents="B2\n")
    result = runner.invoke(ascmhl.commands.diff, ["/root/", "-l"])
    assert (
        result.output
        == """/root/A/AA/ignore.txt | None | Ignored | None | 4.00 B | None
/root/A/AA | 5 | Available | None | 0.00 B | None
/root/A/_A1.txt | 5 | Available | A1.txt | 3.00 B | 3.00 B
/root/B/B1.txt | 3 | Available | None | 3.00 B | 3.00 B
/root/_B/B3.txt | None | New | None | 3.00 B | None
/root/A | 5 | Available | None | 0.00 B | None
/root/B | 3 | Available | None | 0.00 B | None
/root/Stuff.txt | 2 | Available | None | 6.00 B | 6.00 B
/root/_B | None | New | None | 0.00 B | None
/root/A/AA/__AA1.txt | 5 | Missing | AA/_AA1.txt, AA/AA1.txt | None | 4.00 B
"""
    )
    assert result.exit_code == 0
