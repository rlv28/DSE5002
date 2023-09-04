#call libraries
library(dplyr)
library(tidyverse)
library(ggplot2)

#read data
data_science_salary_df <- read.csv("R Project/data.csv"
                                   ,stringsAsFactors=FALSE)

#review data
summary (data_science_salary_df)


#returning only full time positions. Since we don't know how many hours 
#the part time, contract and freelance positions worked the units of 
#their salaries are not comparable to the full time units 

data_science_salary_ft_df = data_science_salary_df[
  data_science_salary_df$employment_type == 'FT',]

#change money to 2023 dollars using SSA AWI values. 
#Increase from:
#2020 to 2021: 8.89%
#2021 to 2022: 4.8%
#2022 to 2023: 4.2%
#source: 
#https://www.ssa.gov/oact/TR/TRassum.html and 
#https://www.ssa.gov/oact/cola/awidevelop.html

dollars_in_2023_df <-data.frame(
  X = data_science_salary_ft_df$X,
  dollars_in_2023=c(1:length(data_science_salary_ft_df$work_year)))

for(i in 1:length(data_science_salary_ft_df$work_year)) {
  if (data_science_salary_ft_df$work_year[i] == 2020){
    dollars_in_2023_df[i,2] <- data_science_salary_ft_df$salary_in_usd[i]*1.089*1.048*1.042
    }else if (data_science_salary_ft_df$work_year[i] == 2021){
    dollars_in_2023_df[i,2] <- data_science_salary_ft_df$salary_in_usd[i]*1.048*1.042
    }else if (data_science_salary_ft_df$work_year[i] == 2022){
    dollars_in_2023_df[i,2] <- data_science_salary_ft_df$salary_in_usd[i]*1.042
    }
  }

#join salary in 2023 dollars to df
data_science_salary_ft_2023_df <- data_science_salary_ft_df %>%
  full_join(dollars_in_2023_df, by="X")

#create labels for experience_levels:
#EN Entry-level / Junior MI Mid-level / Intermediate SE Senior-level / Expert EX Executive-level / Director

experience_level_labels <- c("Entry-level\n\ or\n\ Junior", "Mid-level\n\ or\n\ Intermediate", 
                    "Senior-level\n\ or\n\ Expert", "Executive-level\n\ or\n\ Director")
names(experience_level_labels) <- c("EN", "MI", "SE", "EX")


#plot overall landscape of salaries by experience level
ggplot(data_science_salary_ft_2023_df) +
  geom_point(aes(x=X,y=dollars_in_2023), color = 'blue') +
  facet_grid(~factor(experience_level, 
                     levels=c('EN', 'MI', 'SE', 'EX')), 
                     labeller = as_labeller(experience_level_labels))+
  scale_y_continuous(labels=scales::dollar_format())+
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(title='Salary by Experience Level',  
         y='Salary in 2023 USD',
       x=element_blank())

#summary of overall picture by experience level  
data_science_salary_ft_2023_df %>% 
  group_by(experience_level) %>%
  summarize(average_salary = mean(dollars_in_2023),
            quartiles=list(quantile(dollars_in_2023)) ) %>%
  unnest_wider(quartiles)


#plot overall DS landscape as boxplots by experience level
    #change experience_level to a factor

data_science_salary_ft_2023_df$experience_level <- 
  factor(data_science_salary_ft_2023_df$experience_level, levels = c("EN", "MI", "SE", "EX"))
  

ggplot(data_science_salary_ft_2023_df, 
       mapping = aes(x='', y= dollars_in_2023, fill=experience_level)) +
  geom_boxplot() +
  scale_y_continuous(labels=scales::dollar_format()) +
  scale_fill_discrete(name = "Experience Level", labels=experience_level_labels) +
  labs(title='Salary by Experience Level',  
       y='Salary in 2023 USD',
       x=element_blank())

#Summary of values from boxplot
box_plot_summary_full_data <- data_science_salary_ft_2023_df %>%
  group_by(experience_level) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))


#look at the salary by remote level

summary_for_remote(data_science_salary_ft_2023_df)

ggplot(data_science_salary_ft_2023_df) +
  geom_point(aes(x=X,y=dollars_in_2023)) +
  facet_grid(~factor(remote_ratio))+ 
  scale_y_continuous(labels=scales::dollar_format())+
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(title='Salary by Remote Ratio',  
       y='Salary in 2023 USD',
       x=element_blank())


box_plot_summary_company_size_full_data <- data_science_salary_ft_2023_df %>%
  group_by(company_size) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))

######just remote level did not show much of use###########


#Consider remote level and company size

#change company_size to a factor and create labels

data_science_salary_ft_2023_df$company_size <- 
  factor(data_science_salary_ft_2023_df$company_size, levels = c("S", "M", "L"))

company_size_labels <- c("Small", "Medium", "Large" )
names(company_size_labels) <- c("S", "M", "L")


#summary for remote and experice
summary_for_remote_and_experience(data_science_salary_ft_2023_df)


#graph of 
ggplot(data_science_salary_ft_2023_df) +
  geom_point(aes(x=X,y=dollars_in_2023)) +
  facet_grid(.~remote_ratio + company_size)+ 
  scale_y_continuous(labels=scales::dollar_format())+
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(title='Salary by Remote Ratio and Company Size',  
       y='Salary in 2023 USD',
       x=element_blank())



ggplot(data_science_salary_ft_2023_df, 
       mapping = aes(x='', y= dollars_in_2023), color=remote_ratio) +
  facet_grid(.~company_size +remote_ratio, 
             labeller = labeller(company_size = company_size_labels, 
                                 remote_ratio = c("0" = "0%-20%", "50" = "20%-80%", "100" = "80%-100%"))) +
  geom_boxplot() +
  scale_y_continuous(labels=scales::dollar_format()) +
  labs(title='Salary by Company Size and Remote Ratio',  
       y='Salary in 2023 USD',
       x=element_blank())

box_plot_summary_company_size_and_remote_full_data <- data_science_salary_ft_2023_df %>%
  group_by(company_size, remote_ratio) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))

 



#data based on just company size


summary_for_company_size(data_science_salary_ft_2023_df)

ggplot(data_science_salary_ft_2023_df) +
  geom_point(aes(x=X,y=dollars_in_2023), color="blue") +
  facet_grid(.~company_size)+ 
  scale_y_continuous(labels=scales::dollar_format())+
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(title='Salary by Company size',  
       y='Salary in 2023 USD',
       x=element_blank())


# data based on whether the employee lives in the US.

#create column of data and join to df stating whether they reside in the US

live_in_US_df <-data.frame(
  X = data_science_salary_ft_df$X,
  live_in_US=c(data_science_salary_ft_df$employee_residence == "US"))

data_science_salary_ft_2023_df <- data_science_salary_ft_2023_df %>%
  full_join(live_in_US_df, by="X")

data_science_salary_ft_2023_df$live_in_US <- 
  factor(data_science_salary_ft_2023_df$live_in_US, levels = c(TRUE, FALSE))


live_in_US_label <- c('Lives in the US', "Lives outside the US")
names(live_in_US_label) <- c(TRUE, FALSE)

#graph of salary based on whether employee lives in the US

ggplot(data_science_salary_ft_2023_df) +
  geom_boxplot(aes(x=X,y=dollars_in_2023), color = 'blue') +
  facet_grid(.~live_in_US, labeller = labeller(live_in_US = live_in_US_label))+
  scale_y_continuous(labels=scales::dollar_format())+
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(title="Salary based on Employee Residence in the US",
       y='Salary in 2023 USD',
       x=element_blank())

box_plot_summary_residency <- data_science_salary_ft_2023_df %>%
  group_by(live_in_US) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))


summary_for_residency(data_science_salary_ft_2023_df)



########################look at just SE level##########################
#Filter date for SE

data_science_salary_ft_2023_df_se <- data_science_salary_ft_2023_df %>%
  filter(experience_level == "SE")

#remote level

summary_for_remote(data_science_salary_ft_2023_df_se)

box_plot_summary_company_size_and_remote_full_data_se <- data_science_salary_ft_2023_df_se %>%
  group_by(company_size, remote_ratio) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))
#Consider remote level and company size



box_plot_summary_company_size_and_remote_full_data_se <- 
  data_science_salary_ft_2023_df_se %>%
  group_by(company_size, remote_ratio) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))


######sample size too small, values did not make sense######


#data based on just company size


summary_for_company_size(data_science_salary_ft_2023_df_se)


box_plot_summary_company_size_data_se <- 
  data_science_salary_ft_2023_df_se %>%
  group_by(company_size) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))
# data based on whether the employee lives in the US.


box_plot_summary_residency_se <- data_science_salary_ft_2023_df_se %>%
  group_by(live_in_US) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))


summary_for_residency(data_science_salary_ft_2023_df_se)


########################Sorting by job title:##########################

#look at the titles in the data

unique(data_science_salary_df$job_title)

#look at First recommendation of data science engineer or analytics engineer
#filter job titles

dse_or_ae_ft_df <- data_science_salary_ft_2023_df %>%
  filter(job_title == "Analytics Engineer" | 
           job_title == "Data Analytics Engineer"|
           job_title == "Data Science Engineer" |
           job_title == "Head of Data")

#plot of first recommendation data

graph_for_data(dse_or_ae_ft_df, 
              'Salary by Experience Level for\n\ Data Engineers and Analytics Engineers',
               .~experience_level,  as_labeller(experience_level_labels))

summary_for_data(dse_or_ae_ft_df )

summary_for_remote(dse_or_ae_ft_df)
summary_for_remote_and_experience(dse_or_ae_ft_df)
summary_for_company_size(dse_or_ae_ft_df)
summary_for_residency(dse_or_ae_ft_df)

###### do to small sample size the trends viewed above seem inaccurate###

#Second possibility of hiring a data scientist
ds_ft_df <- data_science_salary_ft_2023_df %>%
  filter(job_title == "Data Scientist" | 
           job_title == "Lead Data Scientist"|
           job_title == "Data Science Manager"|
           job_title == "Applied Data Scientist" |
           job_title == "Director of Data Science" |
           job_title == "Principal Data Scientist" |
           job_title == "Head of Data Science")

graph_for_data(ds_ft_df, 
               'Salary by Experience Level for\n\ Data Scientist')
summary_for_data(ds_ft_df )

#boxplot for reccomendation 2 because of outliers
box_plot_summary_ds_df <- ds_ft_df %>%
  group_by(experience_level) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))



summary_for_remote(ds_ft_df)
summary_for_remote_and_experience(ds_ft_df)
summary_for_country(ds_ft_df)
summary_for_residency(ds_ft_df)


#third possibility of hiring a data engineer
de_ft_df <- data_science_salary_ft_2023_df %>%
  filter(job_title == "Lead Data Engineer" | 
           job_title == "Data Engineer"|
           job_title == "Data Engineering Manager"|
           job_title == "Principal Data Engineer")

graph_for_data(de_ft_df, 
               'Salary by Experience Level for\n\ Data Engineer')
summary_for_data(de_ft_df )  

#boxplot for third possibility bc of outliers
box_plot_summary_de_df <- de_ft_df %>%
  group_by(experience_level) %>%
  summarise(boxplot.stats(dollars_in_2023,coef=1.5))



summary_for_remote(de_ft_df )
summary_for_remote_and_experience(de_ft_df )
summary_for_country(de_ft_df )
summary_for_residency(de_ft_df )








########UDF for data analysis#############


graph_for_data <- function(df, title, group_factor, labeller_names){
  #function to plot salary grouped by experience level
  point_plot <- ggplot(df) +
    geom_point(aes(x=X,y=dollars_in_2023), color = 'blue') +
    facet_grid(group_factor, labeller=labeller_names )+
    scale_y_continuous(labels=scales::dollar_format())+
    theme(axis.text.x=element_blank(),
          axis.ticks.x=element_blank())+
    labs(title=title,
         y='Salary in 2023 USD',
         x=element_blank())
  
  return(point_plot)
  
}


summary_for_data <- function(df){
  #function to calculate overall summary statistics grouped by experience level
 summary_df <- df %>%
    group_by(experience_level) %>%
    summarize(average_salary = mean(dollars_in_2023),
              quartiles=list(quantile(dollars_in_2023)) ) %>%
    unnest_wider(quartiles)
  return(summary_df)
 
}

summary_for_remote <- function(df){
  #function to calculate summary statistics grouped by remote level
  summary_df <- df %>%
  group_by(remote_ratio) %>%
    summarize(average_salary = mean(dollars_in_2023),
              quartiles=list(quantile(dollars_in_2023)) ) %>%
    unnest_wider(quartiles)
  return(summary_df)
  
}

summary_for_remote_and_experience <- function(df){
  #function to calculate summary statistics grouped by remote level
  summary_df <- df %>%
  group_by(remote_ratio, experience_level) %>%
    summarize(average_salary = mean(dollars_in_2023),
              quartiles=list(quantile(dollars_in_2023)) ) %>%
    unnest_wider(quartiles)
  return(summary_df)
  
}

summary_for_residency <- function(df){
  #function to calculate summary statistics grouped by whether the employee 
  #resides in the US
  summary_df <- df %>%
  group_by(employee_residence == 'US') %>%
    summarize(average_salary = mean(dollars_in_2023),
              quartiles=list(quantile(dollars_in_2023)) ) %>%
    unnest_wider(quartiles)
  return(summary_df)
  
}

summary_for_company_size <- function(df){
  #function to calculate summary statistics grouped by employee residence
  summary_df <- df %>%
  group_by(company_size) %>%
    summarize(average_salary = mean(dollars_in_2023),
              quartiles=list(quantile(dollars_in_2023)) ) %>%
    unnest_wider(quartiles)
  return(summary_df)
  
}

