setwd("C:/Python27")
getwd()

data <- read.csv(file="regressionData_francisco.tsv", head=TRUE, sep='\t')
dataAN <- read.csv(file="regressionData_armen.tsv", head=TRUE, sep='\t')

attach(data)
library(rpart)
#mylogit <- glm(scopeLabel ~ normNumEmails + theta + normDuration + numSharedDomains + numAddresses + normEntropy + daysSinceLastContact, family="binomial")
mylogit <- glm(scopeLabel  ~normDuration, family="binomial")
myrpart <- rpart(scopeLabel ~ normNumEmails + theta + normDuration + numSharedDomains + numAddresses + normEntropy + daysSinceLastContact)
table(predict(mylogit,type="response")>0.5,data$scopeLabel)
table(predict(myrpart)>0.4, scopeLabel)

print(summary(mylogit))

print(confint(mylogit))

print(anova(mylogit, test="Chisq"))

fit <- predict(mylogit, type="response")
lines(lowess(normEntropy, y=fit))

plot(data$scopeLabel ~ data$normEntropy)
plot(dataAN$scopeLabel ~ dataAN$normEntropy)

plot(data$scopeLabel ~ data$normNumEmails)
plot(dataAN$scopeLabel ~ dataAN$normNumEmails)


# lines(normEntropy, mylogit$fitted, type="l", col="red")
