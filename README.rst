# Witchcrafted

A modding tool for masterduel.

Why witchcrafted? Well happens to be my favourite archetype when I wrote this
probably in 6 months I will have a new pet deck and I will want regret naming
it this. But I do like that it is kinda on theme with the crafted part of the name.

## Giants

Like all apps we stand on the shoulders of the giants in our community.
Some but not all are listed herein. (If this needs updating with anything
give me a shout)

The capability to edit the Unity files comes from the work of UnityPy
which is based on AssetExtractor. Since I am based in macos world, I am
locked out of most unity editors like UABEA and UnityEx so I really am
glad that UnityPy exists.

The lists used to find certain files for editing were created by RndUser
on Nexus and I do recommend you check out their modding guide there too.

## Limits

So as I said this uses UnityPy for the inner working, which means I can only
edit as much as UnityPy allows me to. Which right now is:
- Texture2D
- Sprite(indirectly via linked Texture2D)
- TextAsset
- MonoBehaviour (and all other types that you have the typetree of)

Seems like other assets are on the roadmap and once UnityPy has other capabilities
I see if I can update. Or you can PR it you know.
