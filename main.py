import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import recall_score, precision_score, f1_score, accuracy_score

# Read in data
file = 'Churn_Modelling.csv'
df_original = pd.read_csv(file)

# Check class balance
print("Class balance:\n", df_original['Exited'].value_counts())

# Calculate average balance of customers who churned
avg_churned_bal = df_original[df_original['Exited'] == 1]['Balance'].mean()
print(f"Average balance of churned customers: {avg_churned_bal:.2f}")

# Create a new df that drops RowNumber, CustomerId, Surname, and Gender cols
churn_df = df_original.drop(['RowNumber', 'CustomerId', 'Surname', 'Gender'], axis=1)
churn_df = pd.get_dummies(churn_df, drop_first=True)

# Define the y (target) variable
y = churn_df['Exited']

# Define the X (predictor) variables
X = churn_df.drop('Exited', axis=1)

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)

# Instantiate the model
decision_tree = DecisionTreeClassifier(random_state=42)

# Fit the model to training data
decision_tree.fit(X_train, y_train)

# Make predictions on test data
dt_pred = decision_tree.predict(X_test)

# Generate performance metrics
print("\nPerformance Metrics:")
print("Accuracy:", "%.3f" % accuracy_score(y_test, dt_pred))
print("Precision:", "%.3f" % precision_score(y_test, dt_pred))
print("Recall:", "%.3f" % recall_score(y_test, dt_pred))
print("F1 Score:", "%.3f" % f1_score(y_test, dt_pred))

# Generate confusion matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, dt_pred, labels=decision_tree.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=decision_tree.classes_)
disp.plot()
plt.show()

# Plot the tree
plt.figure(figsize=(15, 12))
plot_tree(decision_tree, max_depth=2, fontsize=14, feature_names=X.columns, class_names={0: 'stayed', 1: 'churned'}, filled=True)
plt.show()

# Import GridSearchCV
from sklearn.model_selection import GridSearchCV

# Assign a dictionary of hyperparameters to search over
tree_para = {'max_depth': [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 30, 40, 50],
             'min_samples_leaf': [2, 5, 10, 20, 50]}

# Assign a dictionary of scoring metrics to capture
scoring = {'accuracy', 'precision', 'recall', 'f1'}

# Instantiate the classifier
tuned_decision_tree = DecisionTreeClassifier(random_state=42)

# Instantiate the GridSearch
clf = GridSearchCV(tuned_decision_tree, tree_para, scoring=scoring, cv=5, refit="f1")

# Fit the model
clf.fit(X_train, y_train)

# Examine the best model from GridSearch
print("\nBest Estimator:", clf.best_estimator_)
print("Best Avg. Validation Score: ", "%.4f" % clf.best_score_)

# Function to create a results table
def make_results(model_name, model_object):
    '''
    Accepts as arguments a model name (string) and a fit GridSearchCV model object.
    Returns a pandas df with the F1, recall, precision, and accuracy scores
    for the model with the best mean F1 score across all validation folds.
    '''
    # Get all the results from the CV and put them in a df
    cv_results = pd.DataFrame(model_object.cv_results_)
    # Isolate the row of the df with the max(mean f1 score)
    best_estimator_results = cv_results.loc[cv_results['mean_test_f1'].idxmax(), :]
    # Extract accuracy, precision, recall, and f1 score from that row
    f1 = best_estimator_results['mean_test_f1']
    recall = best_estimator_results['mean_test_recall']
    precision = best_estimator_results['mean_test_precision']
    accuracy = best_estimator_results['mean_test_accuracy']
    # Create table of results
    table = pd.DataFrame({'Model': [model_name],
                           'F1': [f1],
                           'Recall': [recall],
                           'Precision': [precision],
                           'Accuracy': [accuracy]})
    return table

# Call the function on our model
result_table = make_results("Tuned Decision Tree", clf)
print("\nResults Table:")
print(result_table)

# Save results table as csv
result_table.to_csv("Results.csv", index=False)
