from celery_poc.main import (
    greetings,
    read_file_content,
    write_file_content,
    create_directory,
    list_files_in_directory,
    copy_file,
)


def test_greetings():
    """Test the greetings function returns hello world message."""
    result = greetings()
    assert result == "Hello, World!"


def test_data_directory_access(test_data_dir):
    """Test that we can access the test data directory and perform file operations."""
    # Test basic directory access
    assert test_data_dir.exists()
    assert test_data_dir.is_dir()
    assert test_data_dir.name == "data"

    # Test that we can find the test data file
    sample_file = test_data_dir / "sample.txt"
    assert sample_file.exists()
    assert sample_file.is_file()

    # Test reading the test data file
    content = read_file_content(sample_file)
    assert "Hello, World!" in content
    assert "test data file" in content

    # Test listing files in data directory
    files = list_files_in_directory(test_data_dir)
    assert len(files) >= 1
    assert sample_file in files


def test_file_operations_with_temp_directory(temp_dir, test_data_dir):
    """Test file operations using temporary directory."""
    with temp_dir() as temp_path:
        # Copy fake data file from test data directory to temp directory
        source_file = test_data_dir / "sample.txt"
        destination_file = temp_path / "copied_sample.txt"
        copy_file(source_file, destination_file)

        # Verify the file was copied and content is correct
        assert destination_file.exists()
        assert read_file_content(destination_file) == read_file_content(source_file)

        # Test writing and reading files
        test_file = temp_path / "test.txt"
        content = "Hello from temp directory!"
        write_file_content(test_file, content)

        # Verify the file was created and content is correct
        assert test_file.exists()
        assert read_file_content(test_file) == content

        # Test creating directories
        subdir = temp_path / "subdir"
        create_directory(subdir)
        assert subdir.exists()
        assert subdir.is_dir()

        # Test listing files (should have 2 files now)
        files = list_files_in_directory(temp_path)
        assert len(files) == 2
        assert destination_file in files
        assert test_file in files
