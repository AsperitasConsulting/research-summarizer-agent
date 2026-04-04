# Commands used to instruct agents

## Prerequisites

### Claude Code install

Install [Claude Code](https://code.claude.com/docs/en/quickstart#step-1-install-claude-code) and execute the command below:

```
claude --dangerously-skip-permissions
```

### RuFlo Workstation Install
```
npm install -g ruflo
```

## Command Templates

### RuFlo Project Installation

```
npx ruflo init
npx ruflo init upgrade --add-missing
```

> HiveMind initialization

The command below initializes your team and starts a wizard.  Choose the `Hierarchical Mesh` and `Byzantine Fault Tolerant` optons.
```
npx ruflo hive-mind init
```

### RuFlo Command template for research.  Queen types are strategic, tactical, adaptive

```
npx ruflo hive-mind spawn "" --queen-type strategic --claude
```

## Claude Code agent teams

Simply preface any instructions with "Create an agent team to...."