# Witchcrafted

A modding tool for masterduel.

Why witchcrafted? Well happens to be my favourite archetype when I wrote this
probably in 6 months I will have a new pet deck and I will want regret naming
it this. But I do like that it is kinda on theme with the crafted part of the name.

Why not insert [another general unity editor]? This is meant to make it
easy to mod MD you don't have to understand unity or the data structure
just make the edits you want.

## Capabilities/Todo

Things I'd like to be able to do

- Extract Card Art [x]
- Import Card Art [x]
- Edit Summon Animations [ ]
- Edit Card Names [ ]
- Edit Card Descriptions [ ]
- Edit UI assets [ ]
- Extract/Import decks list [ ] (Not sure if it possible)
- Extract info on recent duels [ ] (Not sure if possible)
  - Would love this for my own stats.
  - If can get this working might want to work up
    some sort of AI deck classification to create matchup tables
    and share data with other users

## PRs please

Would love some help with this, I like playing MD and modding/coding
in general but never have the time. Any contributions welcome.

## Duel Links?

The code is mostly the same in Duel Links as in master duel it will
probably work fine but haven't tested it.

### Shout Outs

Like all apps we stand on the shoulders of the giants in our community.
Some but not all are listed herein. (If this needs updating with anything
give me a shout)

The capability to edit the Unity files comes from the work of UnityPy
which is based on AssetExtractor. Since I am based in macos world, I am
locked out of most unity editors like UABEA and UnityEx so I really am
glad that UnityPy exists.

The lists used to find certain files for editing were created by RndUser
on Nexus and I do recommend you check out their modding guide there too.

### Limits

So as I said this uses UnityPy for the inner working, which means I can only
edit as much as UnityPy allows me to. Which right now is:

- Texture2D
- Sprite(indirectly via linked Texture2D)
- TextAsset
- MonoBehaviour (and all other types that you have the typetree of)

Seems like other assets are on the roadmap and once UnityPy has other capabilities
I will see if I can update. Or you can PR it you know.
