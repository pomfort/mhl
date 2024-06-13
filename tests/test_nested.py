"""
__author__ = "Katharina Böttcher"
__copyright__ = "Copyright 2024, Pomfort GmbH"

__license__ = "MIT"
__maintainer__ = "Patrick Renner, Alexander Sahm"
__email__ = "opensource@pomfort.com"
"""

import os
import shutil

from click.testing import CliRunner
from freezegun import freeze_time

import ascmhl


@freeze_time("2020-01-16 09:15:00")
def test_create_nested_succeed(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/A2.txt", contents="A2\n")
    fs.create_file("/root/C/C1.txt", contents="A2\n")
    fs.create_file("/root/A/AA/AA1.txt", contents="AA1\n")
    os.mkdir("/root/emptyFolderA")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/AA", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/A/AA/ascmhl/0001_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/B/ascmhl/0001_B_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/B/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/0002_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/ascmhl/ascmhl_chain.xml")
    with open("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl", "r") as fin:
        fileContents = fin.read()
        assert "0002_AA_2020-01-16_091500Z.mhl" in fileContents
        assert "B/ascmhl/0002_B_2020-01-16_091500Z.mhl" in fileContents
        assert "AA1.txt" not in fileContents
        assert "C1.txt" in fileContents

    fs.create_file("/root/A/AA/AA2.txt", contents="AA2\n")
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/A/AA/ascmhl/0003_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/ascmhl/0002_root_2020-01-16_091500Z.mhl")
    assert not os.path.exists("/root/ascmhl/0003_B_2020-01-16_091500Z.mhl")
    with open("/root/ascmhl/0002_root_2020-01-16_091500Z.mhl", "r") as fin:
        fileContents = fin.read()
        assert "0003_AA_2020-01-16_091500Z.mhl" in fileContents
        assert "AA2.txt" not in fileContents

    # test history command
    result = runner.invoke(ascmhl.commands.info, ["/root"])
    assert "Child History at /root/A/AA:" in result.output
    assert result.output.count("Generation 3") == 2
    assert result.output.count("Generation 2") == 3


@freeze_time("2020-01-16 09:15:00")
def test_create_nested_mhl_file_modified(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/A2.txt", contents="A2\n")
    fs.create_file("/root/C/C1.txt", contents="A2\n")
    fs.create_file("/root/A/AA/AA1.txt", contents="AA1\n")
    os.mkdir("/root/emptyFolderA")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/AA", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/A/AA/ascmhl/0001_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/B/ascmhl/0001_B_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/B/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/0002_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/ascmhl/ascmhl_chain.xml")
    with open("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl", "r") as fin:
        fileContents = fin.read()
        assert "0002_AA_2020-01-16_091500Z.mhl" in fileContents
        assert "B/ascmhl/0002_B_2020-01-16_091500Z.mhl" in fileContents
        assert "AA1.txt" not in fileContents
        assert "C1.txt" in fileContents

    fs.create_file("/root/A/AA/AA2.txt", contents="AA2\n")

    with open("/root/A/AA/ascmhl/0002_AA_2020-01-16_091500Z.mhl", "a") as mhl_file:
        mhl_file.write("changed content")
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert result.exception
    assert result.exit_code == 31


@freeze_time("2020-01-16 09:15:00")
def test_create_nested_mhl_file_missing(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/A2.txt", contents="A2\n")
    fs.create_file("/root/C/C1.txt", contents="A2\n")
    fs.create_file("/root/A/AA/AA1.txt", contents="AA1\n")
    os.mkdir("/root/emptyFolderA")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/AA", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/A/AA/ascmhl/0001_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/B/ascmhl/0001_B_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/B/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/0002_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/ascmhl/ascmhl_chain.xml")
    with open("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl", "r") as fin:
        fileContents = fin.read()
        assert "0002_AA_2020-01-16_091500Z.mhl" in fileContents
        assert "B/ascmhl/0002_B_2020-01-16_091500Z.mhl" in fileContents
        assert "AA1.txt" not in fileContents
        assert "C1.txt" in fileContents

    fs.create_file("/root/A/AA/AA2.txt", contents="AA2\n")

    os.remove("/root/A/AA/ascmhl/0001_AA_2020-01-16_091500Z.mhl")
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert result.exception
    assert result.exit_code == 33

    result = runner.invoke(ascmhl.commands.diff, ["/root"])
    assert result.exception
    assert result.exit_code == 33


@freeze_time("2020-01-16 09:15:00")
def test_create_nested_mhl_chain_missing(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/A2.txt", contents="A2\n")
    fs.create_file("/root/C/C1.txt", contents="A2\n")
    fs.create_file("/root/A/AA/AA1.txt", contents="AA1\n")
    os.mkdir("/root/emptyFolderA")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/AA", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/A/AA/ascmhl/0001_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/B/ascmhl/0001_B_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/B/ascmhl/ascmhl_chain.xml")

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception
    assert os.path.exists("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/A/AA/ascmhl/0002_AA_2020-01-16_091500Z.mhl")
    assert os.path.exists("/root/ascmhl/ascmhl_chain.xml")
    with open("/root/ascmhl/0001_root_2020-01-16_091500Z.mhl", "r") as fin:
        fileContents = fin.read()
        assert "0002_AA_2020-01-16_091500Z.mhl" in fileContents
        assert "B/ascmhl/0002_B_2020-01-16_091500Z.mhl" in fileContents
        assert "AA1.txt" not in fileContents
        assert "C1.txt" in fileContents

    fs.create_file("/root/A/AA/AA2.txt", contents="AA2\n")
    os.remove("/root/A/AA/ascmhl/ascmhl_chain.xml")
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert result.exception
    assert result.exit_code == 32

    result = runner.invoke(ascmhl.commands.diff, ["/root"])
    assert result.exception
    assert result.exit_code == 32


@freeze_time("2020-01-16 09:15:00")
def test_deleted_ascmhl_folder(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/", "-h", "xxh64", "-v"])
    assert not result.exception

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception

    shutil.rmtree("/root/B/ascmhl")

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert result.exception
    assert result.exit_code == 30
    assert not os.path.exists("/root/ascmhl/0002_root_2020-01-16_091500Z.mhl")

    result = runner.invoke(ascmhl.commands.create, ["/root"])
    assert result.exception
    assert result.exit_code == 30
    assert not os.path.exists("/root/ascmhl/0003_root_2020-01-16_091500Z.mhl")


def test_deleted_ascmhl_folder_diff(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/", "-h", "xxh64", "-v"])
    assert not result.exception

    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception

    shutil.rmtree("/root/B/ascmhl")

    result = runner.invoke(ascmhl.commands.diff, ["/root", "-v"])
    assert result.exception
    assert result.exit_code == 30
    assert not os.path.exists("/root/ascmhl/0002_root_2020-01-16_091500Z.mhl")


@freeze_time("2020-01-16 09:15:00")
def test_new_root_folder(fs):
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A/"])
    result = runner.invoke(ascmhl.commands.create, ["/root/B/"])

    result = runner.invoke(ascmhl.commands.create, ["/root/", "-cr"])

    result = runner.invoke(ascmhl.commands.info, ["/root/"])
    assert not result.exception
    assert (
        result.output
        == """Info with history at path: /root/
  Generation 1 (2020-01-16T09:15:00+00:00)

Child History at /root/A:
  Generation 1 (2020-01-16T09:15:00+00:00)

Child History at /root/B:
  Generation 1 (2020-01-16T09:15:00+00:00)\n"""
    )


@freeze_time("2020-01-16 09:15:00")
def test_create_nested_error_34(fs):
    fs.create_file("/root/Stuff.txt", contents="stuff\n")
    fs.create_file("/root/A/A1.txt", contents="A1\n")
    fs.create_file("/root/B/B1.txt", contents="B1\n")
    fs.create_file("/root/A/A2.txt", contents="A2\n")

    runner = CliRunner()
    result = runner.invoke(ascmhl.commands.create, ["/root/A", "-h", "xxh64", "-v"])
    assert not result.exception
    result = runner.invoke(ascmhl.commands.create, ["/root/B", "-h", "xxh64", "-v"])
    assert not result.exception
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception

    # fs.create_file("/root/A/AA/AA2.txt", contents="AA2\n")
    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v"])
    assert not result.exception

    os.rename("/root/A", "/root/_A")
    os.rename("/root/B/B1.txt", "/root/B/_B1.txt")

    result = runner.invoke(ascmhl.commands.diff, ["/root", "-l", "-v"])
    assert result.exit_code == 34

    result = runner.invoke(ascmhl.commands.create, ["/root", "-h", "xxh64", "-v", "-dr"])
    assert not result.exception
