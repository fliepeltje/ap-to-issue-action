## Usage

Create a workflow file in your .github/workflows directory as follows:

### workflow.yaml


    name: "Workflow"
    on: ["push"]
    jobs:
      build:
        runs-on: "ubuntu-latest"
        steps:
          - uses: "actions/checkout@master"
          - name: "AP to Issue"
            uses: "fliepeltje/ap-to-issue-action"
            id: "ap"
            with:
              TOKEN: ${{ secrets.GITHUB_TOKEN }}


### Inputs

| Input          | Default value                   | Description                                                                                                            |
| -------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `REPO`         | `"${{ github.repository }}"`    | The path to the repository where the action will be used, e.g. 'alstr/my-repo' (automatically set)                     |
| `BEFORE`       | `"${{ github.event.before }}"`  | The SHA of the last pushed commit (automatically set)                                                                  |
| `SHA`          | `"${{ github.sha }}"`           | The SHA of the latest commit (automatically set)                                                                       |
| `TOKEN`        | `"${{ secrets.GITHUB_TOKEN }}"` | The GitHub access token to allow us to retrieve, create and update issues (automatically set)                          |
| `LOOKUP_TABLE` | No default value                | Used to configure lookup table for actual name to gh username, specify as kv pairs `donatas=fliepeltje niels=nielsbom` |

## Examples

### Adding APs

When taking meeting notes, you can specify a point of action with the following syntax:

```md
AP Donatas: Do this important thing
``` 

This will result in creating a new issue for `fliepletje` with the title **Do this important thing**

### Multiline APs

If an action requires a body/description, you can specify this by using indentation. Tabs and spaces work - we don't judge:

```md
AP Donatas: Another imprtant task
    This is a description
```

When specifying multiple action points, a new line is required:
```md
AP Donatas: Bla
    description

AP Donatas: More bla
    more description
```


### Multiple assignees

To specify multiple assignees to an issue, use the `|` operator:
```md
AP Donatas|Niels: Do this together
```

