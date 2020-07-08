# Stormtorch's Pippet Bot
A Discord bot used to simulate the online math game Prodigy.

*Note: Some folders, such as those containing images, fonts, and logins will not be shown here for convinience.*

## Pippet is Exclusive to the Following Discord Servers:
- [Camden Bell Official](https://discord.gg/zuEvEUc)
- [SLounge](https://discord.gg/QqecbRm)
- [Pippet Support](https://discord.gg/uDk7WSa)

## Basic Commands
To start using Pippet, join one of the servers above and run the following command:
```
pmp start
```
To login to an existing Pippet account, run the following command:
```
pmp login
```
If you are an `Administrator` of one of these servers, you can run the following command to change the prefix:
```
pmp prefix <new prefix>
```
## Calculations

The level of a wizard is calculated from the number of stars the wizard has. The following function represents the conversion, where *x* is the number of stars a wizard has and *f(x)* is the level: **Note that this conversion is only accurate to the real Prodigy game up to 10 wizard levels. Pippet's version gets heavily nerfed from level 50 and up.**
```
f(x) = floor(0.00000000183x³ - 0.0000152x² + 0.0454x + 1.72)
```

Here is the same function in python that has the level as a return value:
```python
def get_level(stars: int):
    level = int(0.00000000183 * stars ** 3 - 0.0000152 * stars ** 2 + 0.0454 * stars + 1.72)
    return level
```
