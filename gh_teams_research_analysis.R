## TopiCS SI Article
## EveryBOTy Counts
## Created September 2019
## Updated April 2022


# Load Packages -----------------------------------------------------------

# wrangling & plotting
library(tidyverse)
library(reshape2)
library(ggpubr)
library(RColorBrewer)

# analysis
library(esc) ## effect sizes
library(coin) ## wilcox_test, using distribution = "exact" to get z for effect size calculation


# Import Data ---------------------------------------------------------------


#setwd("")

df <- read.csv("gh_teams_research_EveryBOTy-counts.csv") %>%
  group_by(name_h) %>%
  mutate(log_productivity = log(work_per_human),
         sqrt_efficiency = sqrt(eval_survival_day_median)) %>%
  ungroup()

df$Team_size_class <- ordered(df$Team_size_class,
                              levels = c("Small",
                                         "Medium",
                                         "Large"))

df$Team_type <- factor(df$Team_type,
                       levels = c("human",
                                  "human-bot"))

# Get Counts for Human Work Event Data -------------------------------------


## keep just people data
humanWork <- df %>%
  dplyr::select("name_h",
                "Team_type", 
                "Team_size_class",
                "human_IssueComments",
                "human_PRReviewComment",
                "human_Push",
                "human_MergedPR")

## check counts and medians by grouping variables
humanWork.counts <- humanWork %>%
  group_by(Team_type) %>%
  summarise(
            sum_IC = sum(human_IssueComments),
            med_IC = median(human_IssueComments),
            sum_PRRC = sum(human_PRReviewComment),
            med_PRRC = median(human_PRReviewComment),
            sum_Push = sum(human_Push),
            med_Push = median(human_Push),
            sum_PR = sum(human_MergedPR),
            med_PR = median(human_MergedPR)
            )


# Gini Distributions by Team Size ----------------------------------------------

## subset the data
#smallt <- df %>%
#  subset(Team_size_class == "Small")
#
#medt <- df %>%
#  subset(Team_size_class == "Medium")
#
#larget <- df %>%
#  subset(Team_size_class == "Large")

## distribution of gini in small teams
#median(smallt$human_gini)
#round(sd(smallt$human_gini), 3)
#
#round(quantile(smallt$human_gini, c(0.025, 0.975)), 3)
#
#ggplot(smallt, aes(x = human_gini)) +
#  geom_density() +
#  geom_rug() 

## distribution of gini in medium teams
#median(medt$human_gini)
#round(sd(medt$human_gini), 3)
#
#round(quantile(medt$human_gini, c(0.025, 0.975)), 3)
#
#ggplot(medt, aes(x = human_gini)) +
#  geom_density() +
#  geom_rug() 

## distribution of gini in large teams
#median(larget$human_gini)
#round(sd(larget$human_gini), 3)
#
#round(quantile(larget$human_gini, c(0.025, 0.975)), 3)
#
#ggplot(larget, aes(x = human_gini)) +
#  geom_density() +
#  geom_rug() 

## distribution of gini in sample
#median(df$human_gini)
#round(sd(df$human_gini), 3)
#
#round(quantile(df$human_gini, c(0.025, 0.975)), 3)
#
#ggplot(df, aes(x = human_gini)) +
#  geom_density() +
#  geom_rug() 


# Inspect and Prep Bot Work Event Data ------------------------------------

## keep only bot data
botWork <- df %>%
  subset(Team_type == "human-bot", 
         select = c("name_h",
                    "Team_size_class",
                    "bot_Push",
                    "bot_IssueComments",
                    "bot_PRReviewComment",
                    "bot_MergedPR")
         )


botWork.counts <- botWork %>%
  group_by(Team_size_class) %>%
  summarise(Push = sum(bot_Push),
            `Issue Comment` = sum(bot_IssueComments),
            `PR Review Comment` = sum(bot_PRReviewComment),
            `Merged PR` = sum(bot_MergedPR)
            )


botWork.longformat <- melt(botWork.counts,
                           id.vars = c("Team_size_class"),
                           measure.vars = c("Push",
                                            "Issue Comment",
                                            "PR Review Comment",
                                            "Merged PR")
                           )



colnames(botWork.longformat)[colnames(botWork.longformat) == "variable"] <- "Work Event"
colnames(botWork.longformat)[colnames(botWork.longformat) == "Team_size_class"] <- "Team Size"
colnames(botWork.longformat)[colnames(botWork.longformat) == "value"] <- "Count"


# Generate Figure for Bot Work Event Counts -------------------------------


#ggsummarystats(
#  botWork.longformat,
#  x = "Work Event",
#  y = "Count",
#  ggfunc = ggbarplot,
#  position = position_dodge(),
#  fill = "Team Size",
#  color = "Team Size",
#  palette = "Paired",
#  legend = "top",
#  ggtheme = theme_light()
#)


png(filename = "figure2_botEventCounts.png",
    width = 2000, height = 1600,
    units = "px", res = 330)
ggplot(botWork.longformat, 
       aes(x = `Work Event`, 
           y = Count, 
           fill = `Team Size`
           )) +
  geom_bar(color = "black",
           position = "dodge", 
           stat = "identity"
           ) +
  geom_text(aes(label = Count),
            position = position_dodge(width = 0.9),
            hjust = 0.5,
            vjust = -0.3,
            family = "Times"
            ) +
  scale_fill_brewer(palette = "Paired") +
  ggtitle(label = "Work Events Completed by Bots") +
  labs(fill = "Team Size") +
  ylim(0, 15000) +
  theme(
    text = element_text(size = 9, family = "Times"),
    axis.text = element_text(size = 8),
    legend.position = c(0.75, 1),
    legend.direction = "horizontal",
    legend.text = element_text(size = 9),
    legend.background = element_rect(color = "gray80"),
    panel.background = element_rect(fill = "white", color = "gray80"),
    panel.grid.minor.y = element_line(color = "gray95"),
    panel.grid.major.y = element_line(color = "gray95"),
    panel.grid.major.x = element_line(color = "gray95")
    )
dev.off()

# Create Color Palette ----------------------------------------------------


## create green and purple palette
cols = c("#7846B4","#82B446")

# Work per Person Plots ---------------------------------------------------


png(filename = "figure3_productivity-by-Type+Size.png",
    width = 2000, height = 1600,
    units = "px", res = 330)
ggplot(df, 
       aes(x = Team_size_class, 
           y = log_productivity, 
           fill = Team_type
           )) +
  geom_boxplot(notch = T) +
  scale_fill_manual(values = cols, 
                    labels = c("Human", "Human-Bot"
                               )) +
  ggtitle(label = "Team Productivity Differences") +
  xlab("Team Size") +
  ylab("Log Transformed Work per Person") +
  labs(fill = "Team Type") +
  geom_signif(y_position = c(7.25, 6.75, 6.75), 
              xmin = c(0.8, 1.8, 2.8), xmax = c(1.2, 2.2, 3.2),
              annotation = c("p < .001", "p < .001", "p < .001"), 
              tip_length = 0.025,
              family = "Times"
              ) +
  theme(
    text = element_text(size = 9, family = "Times"),
    axis.text = element_text(size = 9),
    axis.ticks.x = element_blank(),
    legend.position = c(0.793, 1),
    legend.direction = "horizontal",
    legend.text = element_text(size= 9 ),
    legend.background = element_rect(color = "gray80"),
    panel.background = element_rect(fill = "white", color = "gray80"),
    panel.grid.minor.y = element_line(color = "gray95"),
    panel.grid.major.y = element_line(color = "gray95"),
    panel.grid.major.x = element_line(color = "gray95")
    )
dev.off()


# Work Centralization Plots ---------------------------------------------------


png(filename = "figure4_gini-by-Type+Size.png",
    width = 2100, height = 1400,
    units = "px", res = 330)
ggplot(df, 
       aes(x = Team_size_class, 
           y = human_gini, 
           fill = Team_type
           )) +
  geom_boxplot(notch = T) +
  scale_fill_manual(values = cols, 
                    labels = c("Human", "Human-Bot"
                               )) +
  ggtitle(label = "Work Centralization Differences") +
  xlab("Team Size") +
  ylab("Gini Coefficient") +
  labs(fill = "Team Type") +
  geom_signif(y_position=c(.85, .85), 
              xmin = c(0.8, 1.8), xmax = c(1.2, 2.2),
              annotation = c("p = .004", "p = .008"), 
              tip_length = 0.025,
              family = "Times"
              ) +
  ylim(0, 1) +
  theme(
    text = element_text(size = 9, family = "Times"),
    axis.text = element_text(size = 9),
    axis.ticks.x = element_blank(),
    legend.position = c(0.797, 1),
    legend.direction = "horizontal",
    legend.text = element_text(size= 9 ),
    legend.background = element_rect(color = "gray80"),
    panel.background = element_rect(fill = "white", color = "gray80"),
    panel.grid.minor.y = element_line(color = "gray95"),
    panel.grid.major.y = element_line(color = "gray95"),
    panel.grid.major.x = element_line(color = "gray95")
    )
dev.off()




# Work Efficiency Plots ---------------------------------------------------


## should create issue survival subset with NAs removed

df.efficiency <- df %>%
  subset(eval_survival_day_median != "NA")

png(filename = "figure5_efficiency-by-Type+Size.png",
    width = 2000, heigh = 1100,
    units = "px", res = 330)
ggplot(df.efficiency, 
       aes(x = Team_size_class, 
           y = sqrt_efficiency, 
           fill = Team_type
           )) +
  geom_boxplot(notch = T) +
  scale_fill_manual(values = cols, 
                    labels = c("Human", "Human-Bot")
                    ) +
  ggtitle(label = "Work Efficiency Differences",
          subtitle = "Issue Resolution Time"
          ) +
  xlab("Team Size") +
  ylab("Square Root Transformed \nMedian Number of Days") +
  labs(fill = "Team Type") +
  ylim(0, 17) +
  theme(
    text = element_text(size = 9, family = "Times"),
    plot.subtitle = element_text(face = "italic"),
    axis.text = element_text(size = 9),
    axis.ticks.x = element_blank(),
    legend.position = c(0.788, 1),
    legend.direction = "horizontal",
    legend.text = element_text(size = 9 ),
    legend.background = element_rect(color = "gray80"),
    panel.background = element_rect(fill = "white", color = "gray80"),
    panel.grid.minor.y = element_line(color = "gray95"),
    panel.grid.major.y = element_line(color = "gray95"),
    panel.grid.major.x = element_line(color = "gray95")
    )
dev.off()




# Subset Data for Analysis ------------------------------------------------


small.df <- df %>%
  subset(Team_size_class == "Small") 

med.df <- df %>%
  subset(Team_size_class == "Medium") 

large.df <- df %>%
  subset(Team_size_class == "Large") 



# Work per Person Welch's t-test ------------------------------------------


t.test(log_productivity ~ Team_type,
       data = small.df,
       var.equal = F) 
# t = 4.8087, df = 242.69, p-value = 2.668e-06 // adjusted 5.335410e-06

#  mean in group human mean in group human-bot 
#    3.296804                3.863217 


t.test(log_productivity ~ Team_type,
       data = med.df,
       var.equal = F)
# t = 6.3432, df = 175.25, p-value = 1.856e-09 // adjusted 5.566505e-09

#  mean in group human mean in group human-bot 
#     3.142089                4.057966 


t.test(log_productivity ~ Team_type,
       data = large.df,
       var.equal = F)
# t = 2.5907, df = 107.89, p-value = 0.0109 // adjusted 1.090226e-02

#  mean in group human mean in group human-bot 
#     3.504608                4.015055 

## double check//adjust p-values
out <- do.call("rbind", 
               lapply(split(df, df$Team_size_class), 
                      function(x) t.test(log_productivity~Team_type, var.equal = F,
                                         conf.level = 0.95, x)$p.value)
               )

length(which(out < 0.05))

p.adjust(out, method = "holm")


# Work Centralization t-tests ---------------------------------------------


t.test(human_gini ~ Team_type,
       data = small.df,
       var.equal = F) 
# t = 3.2123, df = 266.67, p-value = 0.001478
# 95 percent confidence interval:
#  -0.10004526 -0.02400893
#  mean in group human mean in group human-bot 
#         0.3153313               0.3773584 


with(small.df, sd(human_gini[Team_type == "human"]))
with(small.df, sd(human_gini[Team_type == "human-bot"]))

t.test(human_gini ~ Team_type,
       data = med.df,
       var.equal = F)
# t = 2.9285, df = 177.81, p-value = 0.003852
# 95 percent confidence interval:
#  -0.10457266 -0.02037526
#  mean in group human mean in group human-bot 
#    0.4329432               0.4954172 

with(med.df, sd(human_gini[Team_type == "human"]))
with(med.df, sd(human_gini[Team_type == "human-bot"]))

t.test(human_gini ~ Team_type,
       data = large.df,
       var.equal = F)
# t = 0.76625, df = 96.877, p-value = 0.4454
# 95 percent confidence interval:
#   -0.07036143  0.03116528
#  mean in group human mean in group human-bot 
#         0.5582349               0.5778330 


with(large.df, sd(human_gini[Team_type == "human"]))
with(large.df, sd(human_gini[Team_type == "human-bot"]))

## double check//adjust p-values
out <- do.call("rbind", 
               lapply(split(df, df$Team_size_class), 
                      function(x) t.test(human_gini~Team_type,var.equal = F,
                                         conf.level = 0.95, x)$p.value)
               )

length(which(out < 0.05))

p.adjust(out, method = "holm")


# Work Efficiency Mann Whitney tests --------------------------------------

small.efficiency <- df.efficiency %>%
  subset(Team_size_class == "Small")

med.efficiency <- df.efficiency %>%
  subset(Team_size_class == "Medium")

large.efficiency <- df.efficiency %>%
  subset(Team_size_class == "Large")

wilcox.test(small.efficiency$sqrt_efficiency ~ small.efficiency$Team_type, conf.int = T)
wilcox.test(med.efficiency$sqrt_efficiency ~ med.efficiency$Team_type, conf.int = T)
wilcox.test(large.efficiency$sqrt_efficiency ~ large.efficiency$Team_type, conf.int = T)



## GET MEDIANS
with(small.efficiency, median(sqrt_efficiency[Team_type == "human"])) 
with(small.efficiency, median(sqrt_efficiency[Team_type == "human-bot"]))

with(med.efficiency, median(sqrt_efficiency[Team_type == "human"]))
with(med.efficiency, median(sqrt_efficiency[Team_type == "human-bot"]))

with(large.efficiency, median(sqrt_efficiency[Team_type == "human"]))
with(large.efficiency, median(sqrt_efficiency[Team_type == "human-bot"]))


out <- do.call("rbind", 
               lapply(split(df.efficiency, df.efficiency$Team_size_class), 
                      function(x) wilcox.test(sqrt_efficiency~Team_type,
                                         conf.level = 0.95, x)$p.value)
               )

length(which(out < 0.05))

p.adjust(out, method = "holm")


# Effect Sizes ------------------------------------------------------------

## Work per Person (log productivity analysis)

## small teams
esc_mean_sd(grp1m = 3.86, grp1sd = 1.07, grp1n = 128,
            grp2m = 3.3, grp2sd = 0.87, grp2n = 153,
            es.type = "d"
            )

## medium teams
esc_mean_sd(grp1m = 4.06, grp1sd = .96, grp1n = 84,
            grp2m = 3.14, grp2sd = .97, grp2n = 96,
            es.type = "d"
            )

## large teams
esc_mean_sd(grp1m = 4.02, grp1sd = 1.11, grp1n = 92,
            grp2m = 3.51, grp2sd = 1.18, grp2n = 55,
            es.type = "d"
            )


## Work Centralizaion (Gini analysis)

## small teams
esc_mean_sd(grp1m = 0.38, grp1sd = .16, grp1n = 128,
            grp2m = 0.32, grp2sd = .16, grp2n = 153,
            es.type = "d"
            )

## medium teams
esc_mean_sd(grp1m = 0.5, grp1sd = .16, grp1n = 84,
            grp2m = 0.43, grp2sd = .16, grp2n = 96,
            es.type = "d"
            )

## large teams
esc_mean_sd(grp1m = 0.58, grp1sd = 0.13, grp1n = 92,
            grp2m = 0.56, grp2sd = 0.16, grp2n = 55,
            es.type = "d"
            )

## Work Efficiency (sqrt issue survival analysis)

wilcox_test(small.efficiency$sqrt_efficiency ~ small.df$Team_type, distribution = "exact")
# Z = -1.0611, p-value = 0.2908

wilcox_test(med.efficiency$sqrt_efficiency ~ med.df$Team_type, distribution = "exact")
# Z = -1.3672, p-value = 0.1729

wilcox_test(large.efficiency$sqrt_efficiency ~ large.df$Team_type, distribution = "exact")
# Z = 0.10044, p-value = 0.9219

##small
1.0611/sqrt(104)
### medium
1.3672/sqrt(98)
### large
0.10044/sqrt(101)

