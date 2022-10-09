from enum import Enum


class Servers(Enum):
    CONNERY = 1
    MILLER = 10
    COBALT = 13
    EMERALD = 17
    JAEGER = 19
    APEX = 24
    BRIGGS = 25
    SOLTECH = 40


class Factions(Enum):
    VS = 1
    NC = 2
    TR = 3
    NSO = 4

class ItemAddedContext(Enum):
    SellBundle="SellBundle"
    GiveRewardBundleDing="GiveRewardBundle:Ding"
    GiveRewardBundleAchievement="GiveRewardBundle:Achievement"
    GiveRewardBundleMetaGameEvent="GiveRewardBundle:MetaGameEvent"
    GiveRewardBundleMission="GiveRewardBundle:Mission"
    GiveRwardBundleDirective="GiveRewardBundle:Directive"
    GiveRewardBundleItem="GiveRewardBundle:Item"
    GiveRewardBundleNone="GiveRewardBundle:None"
    SkillGrantItemLine="SkillGrantItemLine"
    RequestTrialItemLine="RequestTrialItemLine"
    SkullGrantItem="SkillGrantItem"
    ScriptAddItem="ScriptAddItem"
    GuildBankWithdrawal="GuildBankWithdrawal"
    PcZoneReceiveEscrowPackage="PcZone::ReceiveEscrowPackage"
    RedeemTerminalProxyItem="RedeemTerminalProxyItem"
    GenericTerminalTransaction="GenericTerminalTransaction"
