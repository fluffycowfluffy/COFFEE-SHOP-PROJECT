# Import necesseray libraries
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity

def cafe_recommender(user_prefs_general: dict,
                     user_prefs_atmosphere: list,
                     user_prefs_specials: list) -> pd.DataFrame:
    """
    Return the top recommendation
    based on user preferences
    """
    # Read in the data
    coffeeshop_df = pd.read_csv("data/coffeeshop_df.csv")
    descriptor_df = pd.read_csv("data/descriptor_df.csv")
    reference_df = pd.read_csv("data/reference_df.csv")

    # Find descriptors with the highest counts for atmosphere and specials
    # This can be put to use with the addition of user entries for descriptors in the future
    atmosphere_desc_series = descriptor_df.groupby("cafe_id")["atmosphere_desc"].value_counts()
    specials_desc_series = descriptor_df.groupby("cafe_id")["specials_desc"].value_counts()

    # Get the top three hits for descriptors and save to list
    atmosphere_desc_list = atmosphere_desc_series.groupby(level = 0).apply(lambda id: id.sort_values(ascending = False).head(3).index.get_level_values(1).to_list())
    specials_desc_list = specials_desc_series.groupby(level = 0).apply(lambda id: id.sort_values(ascending = False).head(3).index.get_level_values(1).to_list())

    # Create the models for our descriptor variables
    mlb_atmosphere = MultiLabelBinarizer() 
    mlb_specials = MultiLabelBinarizer()
    
    # Fit the model to atmosphere and specials
    atmosphere_fit = mlb_atmosphere.fit_transform(atmosphere_desc_list)
    specials_fit = mlb_specials.fit_transform(specials_desc_list)

    # Create one MultiLabelBinarizer dataframe for the encoded description variables
    atmosphere_mlb_df = pd.DataFrame(atmosphere_fit,
                                     columns = mlb_atmosphere.classes_,
                                     index = atmosphere_desc_list.index)
    
    specials_mlb_df = pd.DataFrame(specials_fit,
                                   columns = mlb_specials.classes_,
                                   index = specials_desc_list.index)
    
    desc_df_encoded = pd.merge(atmosphere_mlb_df,
                               specials_mlb_df,
                               on = "cafe_id",
                               how = "left")

    # Select categorical columns for one hot encoding
    categorical_columns = coffeeshop_df.select_dtypes(include = ["object"]).columns.tolist()

    # Create and fit the model in order to one hot encode the dataframe
    encoder = OneHotEncoder(sparse_output = False)
    one_hot_fit = encoder.fit_transform(coffeeshop_df[categorical_columns])

    
    # Create the new one hot encoded dataframe
    oh_coffeeshop_df = pd.DataFrame(one_hot_fit, columns = encoder.get_feature_names_out(categorical_columns))

    # Finalize dataframe with one hot encoded variable
    # Drop the categorical columns
    coffeeshop_df_encoded = pd.concat([coffeeshop_df, oh_coffeeshop_df], axis = 1)
    coffeeshop_df_encoded = coffeeshop_df_encoded.drop(categorical_columns, axis = 1)

    # Merge everything on cafe_id; drop price_point_low to avoid multicollinearity
    full_df = pd.merge(coffeeshop_df_encoded,
                       desc_df_encoded,
                       on = "cafe_id",
                       how = "left").drop(columns = ["price_point_low"]).set_index("cafe_id")

    # Vectorize the user's preferences
    user_atmosphere_vect = mlb_atmosphere.transform([user_prefs_atmosphere])[0]
    user_specials_vect = mlb_specials.transform([user_prefs_specials])[0]
    user_general_vect = np.array(list(user_prefs_general.values()))

   # Create one super vector of ALL the preferences; Reshape for math purposes
    user_prefs_vect = np.concatenate([user_general_vect, user_atmosphere_vect, user_specials_vect]).reshape(1, -1)

    # Create copy dataframe to filter by requirements that cannot be compromised on
    sub_df = full_df.copy()

    # Exclude cafés that don't have uncompromisable factors
    for col in ["study_space", "car_req", "gluten_free"]:
        pref = user_prefs_general.get(col)
        if col in "car_req" and pref == 0:
            sub_df = sub_df[sub_df["car_req"] == 0]
        elif col in ["study_space", "gluten_free", "food_menu"] and pref == 1:
            sub_df = sub_df[sub_df[col] == 1]

    # Calculate scores and add it to the dataframe
    user_scores = cosine_similarity(sub_df.values, user_prefs_vect).flatten() 
    sub_df["similarity"] = user_scores
    
    # Sort and return top cafe
    top_match_df = sub_df.sort_values("similarity", ascending=False).head(1)
    top_match = reference_df[reference_df.index.isin(top_match_df.index)]

    return top_match