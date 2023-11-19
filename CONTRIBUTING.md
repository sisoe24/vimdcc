# Contributing

## Getting Started

1. Fork the repository on GitHub
2. Clone the forked repository to your local machine
3. Create a new branch for your feature

## Development

### Adding a new DCC application

To add a new DCC application, you need to create a new class that inherits from the `VimDCC` class. The class expects the script editor widget as an argument. The script editor widget is different for each DCC application, so you need to implement the `get_script_editor` method in your class.


```python
def get_script_editor(self):
    """Function that returns the script editor widget"""

class MyDCC(VimDCC):
    def __init__(self):
        super().__init__(get_script_editor())

```

You also need to implement the `install` method which will be called when the plugin is installed. This method should install the key handlers and any other functionality that is specific to the DCC application.

```python

def install_(self):
    """Function that installs the plugin"""

```

### Extending the plugin

The plugin is designed to be easily extendable. You can add a n

### Testing

The plugin is tested using the [pytest](https://docs.pytest.org/en/latest/) framework. To run the tests, simply run the following command from the root of the repository:

```bash
