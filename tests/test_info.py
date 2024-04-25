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
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64"])

    result = runner.invoke(ascmhl.commands.info, ["-sf", "/root/A/_A1.txt", "-v"])
    assert (
        result.output == """Info with history at path: /root/A
_A1.txt:
  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/_A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
     In previous generations the file was named: A1.txt
  Generation 4 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (verified) 
    /root/A/_A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
Info with history at path: /root/A
A1.txt:
  Generation 1 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
  Generation 2 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (verified) 
    /root/A/A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 95e230e90be29dd6 (original) 
    /root/A/_A1.txt
     CreatorInfo: myHost.local, ascmhl 0.1.dev471+g8b828f7.d20240313
     ProcessInfo: in-place
     File was renamed to _A1.txt\n"""
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
        "  Generation 3 (2020-01-16T09:15:00+00:00) md5: 9eb84090956c484e32cb6c08455a667b (verified)\n"
        "  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 94c399c2a9a21f9a (verified)\n"
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
        "  Generation 3 (2020-01-16T09:15:00+00:00) md5: 9eb84090956c484e32cb6c08455a667b (verified)\n"
        "  Generation 3 (2020-01-16T09:15:00+00:00) xxh64: 94c399c2a9a21f9a (verified)\n"
    )
    assert result.exit_code == 0

@freeze_time("2020-01-16 09:15:00")
def test_info_renamed_file(fs):
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
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-dr"])
    result = runner.invoke(ascmhl.commands.create, ["/root/", "-h", "xxh64"])

    os.remove("/root/A/AA/AA1.txt")
    fs.create_file("/root/_B/B3.txt", contents="B2\n")
    result = runner.invoke(ascmhl.commands.info, ["/root/", "-l"])
    assert result.output == """/root/A/AA/ignore.txt | None | Ignored | Not Renamed | 4.00 B
/root/A/AA | 4 | Available | Not Renamed | 0.00 B
/root/A/_A1.txt | 4 | Renamed | A1.txt | 3.00 B
/root/B/B1.txt | 3 | Available | Not Renamed | 3.00 B
/root/_B/B3.txt | None | New | Not Renamed | 3.00 B
/root/A | 4 | Available | Not Renamed | 0.00 B
/root/B | 3 | Available | Not Renamed | 0.00 B
/root/Stuff.txt | 2 | Available | Not Renamed | 6.00 B
/root/_B | None | New | Not Renamed | 0.00 B
/root/A/AA/AA1.txt | 2 | Missing | Not Renamed | None\n"""
    assert result.exit_code == 0
