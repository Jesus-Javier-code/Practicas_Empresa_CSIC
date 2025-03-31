{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "---\n",
        "title: \"Olympic Games\"\n",
        "format: \n",
        "  dashboard:\n",
        "    orientation: columns\n",
        "    nav-buttons: [github]\n",
        "    github: https://github.com/posit-conf-2024/olympicdash\n",
        "    theme:\n",
        "      - sketchy\n",
        "      - style/olympicdash.scss\n",
        "logo: images/olympics-logo.svg\n",
        "logo-alt: \"Olympics logo with multicolored circles.\"\n",
        "---"
      ],
      "id": "6eb72cc1"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: load-packages\n",
        "from plotnine import *\n",
        "import great_tables as gt\n",
        "import pandas as pd"
      ],
      "id": "load-packages",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: load-data\n",
        "olympics_full = pd.read_csv(\"../data/olympics.csv\", low_memory = False)"
      ],
      "id": "load-data",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: prep-data\n",
        "# Filter for non-NA medals\n",
        "olympics = olympics_full[(olympics_full[\"medal\"].notna())]\n",
        "\n",
        "# Split the team column at \"-\" into two columns\n",
        "split_data = olympics[\"team\"].str.split(\"-\", n = 1, expand = True)\n",
        "olympics.loc[:, \"team\"] = split_data[0]\n",
        "\n",
        "# Reorder the medal column categories\n",
        "olympics[\"medal\"] = pd.Categorical(olympics[\"medal\"], categories = [\"Bronze\", \"Silver\", \"Gold\"])"
      ],
      "id": "prep-data",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# 🌞 Summer Olympics\n"
      ],
      "id": "cc70e569"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: summmer-prep-data\n",
        "summer_olympics = olympics[(olympics[\"season\"] == \"Summer\")]\n",
        "summer_olympics.reset_index(drop=True, inplace=True)"
      ],
      "id": "summmer-prep-data",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Column - Medals by sport and year {width=65%}\n",
        "\n",
        "### Row - Medals by sport {height=60%}\n"
      ],
      "id": "05246673"
    },
    {
      "cell_type": "code",
      "metadata": {
        "title": "Medals by sport"
      },
      "source": [
        "#| label: summer-medals-by-sport\n",
        "\n",
        "# Lump the sport column to top 15 categories, grouping others as Other\n",
        "top_15_sports = summer_olympics[\"sport\"].value_counts().nlargest(15).index\n",
        "summer_olympics[\"sport\"] = summer_olympics[\"sport\"].apply(lambda x: x if x in top_15_sports else \"Other\")\n",
        "\n",
        "# Convert the sport column to a categorical type with order based on frequency, and reverse the order\n",
        "summer_olympics[\"sport\"] = pd.Categorical(summer_olympics[\"sport\"], categories = summer_olympics[\"sport\"].value_counts().index[::-1])\n",
        "\n",
        "# Move the Other category of the sport column to the beginning\n",
        "new_order = [\"Other\"] + [cat for cat in summer_olympics[\"sport\"].cat.categories if cat != \"Other\"]\n",
        "summer_olympics[\"sport\"] = summer_olympics[\"sport\"].cat.reorder_categories(new_order)\n",
        "\n",
        "# Plot\n",
        "(\n",
        "    ggplot(summer_olympics, aes(x = \"sport\", fill = \"medal\")) +\n",
        "    geom_bar() +\n",
        "    coord_flip() +\n",
        "    guides(fill = guide_legend(reverse = True)) +\n",
        "    scale_fill_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) +  \n",
        "    labs(\n",
        "        x = \"\",\n",
        "        y = \"\",\n",
        "        fill = \"Medal\"\n",
        "    ) +\n",
        "    theme_minimal() +\n",
        "    theme(\n",
        "        legend_position = \"inside\",\n",
        "        legend_position_inside = (0.9, 0.2),\n",
        "        legend_direction = \"horizontal\",\n",
        "        legend_background = element_rect(fill = \"white\", color = \"gray\"),\n",
        "        figure_size = (8, 3)\n",
        "    )\n",
        ")"
      ],
      "id": "summer-medals-by-sport",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### Row - Medals by year {height=40%}\n",
        "\n",
        "::: {.card title=\"Medals by year\"}\n",
        "Due to World War II, no olympic games were held in 1940 and 1944.\n"
      ],
      "id": "c728cee6"
    },
    {
      "cell_type": "code",
      "metadata": {
        "title": "Medals by year"
      },
      "source": [
        "#| label: summer-medals-by-year\n",
        "\n",
        "# Count the occurrences of each medal per year\n",
        "summer_olympics_count = summer_olympics.groupby([\"year\", \"medal\"], observed=True).size().reset_index(name = \"n\")\n",
        "\n",
        "# Plot\n",
        "(\n",
        "    ggplot(summer_olympics_count, aes(x = \"year\", y = \"n\")) +\n",
        "    geom_line(aes(color = \"medal\"), size = 0.5) +\n",
        "    geom_point(aes(fill = \"medal\"), size = 2, color = \"white\") + \n",
        "    guides(color = guide_legend(reverse = True)) + \n",
        "    scale_x_continuous(breaks = range(1896, 2020, 8)) + \n",
        "    scale_color_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) + \n",
        "    scale_fill_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) + \n",
        "    labs(x = \"Year\", y = \"\", color = \"Medal\", fill = \"Medal\") + \n",
        "    theme_minimal() + \n",
        "    theme(\n",
        "        legend_position = \"inside\",\n",
        "        legend_position_inside = (0.9, 0.2),\n",
        "        legend_direction = \"horizontal\",\n",
        "        legend_background = element_rect(fill = \"white\", color = \"gray\"),\n",
        "        figure_size = (11, 2)\n",
        "    )\n",
        ")"
      ],
      "id": "summer-medals-by-year",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::\n",
        "\n",
        "## Column - Medals by country {width=35%}\n",
        "\n",
        "### Row - Value boxes {height=30%}\n"
      ],
      "id": "e3307c07"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: summer-calculate-most-medals\n",
        "\n",
        "# Filter for gold medals\n",
        "gold_medals = summer_olympics[summer_olympics['medal'] == 'Gold']\n",
        "# Group by team and count gold medals\n",
        "gold_medal_counts = gold_medals.groupby('team').size()\n",
        "# Find the team with the most gold medals\n",
        "most_gold_medals = gold_medal_counts.idxmax()\n",
        "count_most_gold_medals = gold_medal_counts.max()\n",
        "\n",
        "# Filter for silver medals\n",
        "silver_medals = summer_olympics[summer_olympics['medal'] == 'Silver']\n",
        "# Group by team and count silver medals\n",
        "silver_medal_counts = silver_medals.groupby('team').size()\n",
        "# Find the team with the most silver medals\n",
        "most_silver_medals = silver_medal_counts.idxmax()\n",
        "count_most_silver_medals = silver_medal_counts.max()\n",
        "\n",
        "# Filter for bronze medals\n",
        "bronze_medals = summer_olympics[summer_olympics['medal'] == 'Bronze']\n",
        "# Group by team and count bronze medals\n",
        "bronze_medal_counts = bronze_medals.groupby('team').size()\n",
        "# Find the team with the most bronze medals\n",
        "most_bronze_medals = bronze_medal_counts.idxmax()\n",
        "count_most_bronze_medals = bronze_medal_counts.max()"
      ],
      "id": "summer-calculate-most-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "::: {.valuebox icon=\"award-fill\" color=\"#d4af37\"}\n",
        "Most golds: \n",
        "\n",
        "`{python} str(count_most_gold_medals)`\n",
        "\n",
        "`{python} most_gold_medals`\n",
        ":::\n",
        "\n",
        "::: {.valuebox icon=\"award-fill\" color=\"#c0c0c0\"}\n",
        "Most silvers: \n",
        "\n",
        "`{python} str(count_most_silver_medals)`\n",
        "\n",
        "`{python} most_silver_medals`\n",
        ":::\n",
        "\n",
        "::: {.valuebox icon=\"award-fill\" color=\"#cd7f32\"}\n",
        "Most bronzes: \n",
        "\n",
        "`{python} str(count_most_bronze_medals)`\n",
        "\n",
        "`{python} most_bronze_medals`\n",
        ":::\n",
        "\n",
        "### Row - Tabsets of tables {height=70% .tabset}\n"
      ],
      "id": "e29111df"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: summer-team-total-medals\n",
        "\n",
        "# Count the occurrences of each medal per team\n",
        "summer_olympics_count = summer_olympics.groupby([\"team\", \"medal\"]).size().reset_index(name=\"n\")\n",
        "\n",
        "# Pivot olympics_count to get medals as columns\n",
        "summer_olympics_pivot = summer_olympics_count.pivot_table(index = \"team\", columns = \"medal\", values = \"n\", fill_value = 0)\n",
        "\n",
        "# Calculate the total number of medals\n",
        "summer_olympics_pivot[\"Total\"] = summer_olympics_pivot[[\"Bronze\", \"Gold\", \"Silver\"]].sum(axis=1)\n",
        "\n",
        "# Reset the index and rearrange columns\n",
        "summer_olympics_pivot = summer_olympics_pivot.reset_index()\n",
        "summer_olympics_pivot = summer_olympics_pivot[[\"team\", \"Gold\", \"Silver\", \"Bronze\", \"Total\"]]\n",
        "\n",
        "# Sort by Total medals, then team\n",
        "summer_olympics_sorted_descending = summer_olympics_pivot.sort_values(by=[\"Total\", \"team\"], ascending=[False, True])\n",
        "summer_olympics_sorted_ascending = summer_olympics_pivot.sort_values(by=[\"Total\", \"team\"], ascending=[True, True])\n",
        "\n",
        "# Remove Total\n",
        "summer_olympics_sorted_descending = summer_olympics_sorted_descending[[\"team\", \"Gold\", \"Silver\", \"Bronze\"]]\n",
        "summer_olympics_sorted_ascending = summer_olympics_sorted_ascending[[\"team\", \"Gold\", \"Silver\", \"Bronze\"]]\n",
        "\n",
        "# Rename the team column to Team\n",
        "summer_olympics_sorted_descending.rename(columns={\"team\": \"Team\"}, inplace=True)\n",
        "summer_olympics_sorted_ascending.rename(columns={\"team\": \"Team\"}, inplace=True)\n",
        "\n",
        "# Find top and bottom 30\n",
        "summer_olympics_sorted_descending_top30 = summer_olympics_sorted_descending.head(30)\n",
        "summer_olympics_sorted_descending_top30.reset_index(drop=True, inplace=True)\n",
        "summer_olympics_sorted_ascending_bottom30 = summer_olympics_sorted_ascending.head(30)\n",
        "summer_olympics_sorted_ascending_bottom30.reset_index(drop=True, inplace=True)"
      ],
      "id": "summer-team-total-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "::: {.card title=\"Top 30 total medals\"}\n",
        "Teams sorted in descending order of total medals.\n"
      ],
      "id": "473b0369"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: summer-top-30-medals\n",
        "(\n",
        "    gt.GT(summer_olympics_sorted_descending_top30).data_color(\n",
        "        columns=[\"Gold\", \"Silver\", \"Bronze\"],\n",
        "        palette=\"Oranges\"\n",
        "    )\n",
        ")"
      ],
      "id": "summer-top-30-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::\n",
        "\n",
        "::: {.card title=\"Bottom 30 total medals\"}\n",
        "Teams sorted in ascending order of total medals.\n"
      ],
      "id": "852586fd"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: summer-bottom-30-medals\n",
        "(\n",
        "    gt.GT(summer_olympics_sorted_ascending_bottom30).data_color(\n",
        "        columns=[\"Gold\", \"Silver\", \"Bronze\"],\n",
        "        palette=\"Blues\"\n",
        "    )\n",
        ")"
      ],
      "id": "summer-bottom-30-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::\n",
        "\n",
        "# ❄️ Winter Olympics\n"
      ],
      "id": "29c36dcf"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-prep-data\n",
        "winter_olympics = olympics[(olympics[\"season\"] == \"Winter\")]\n",
        "winter_olympics.reset_index(drop=True, inplace=True)"
      ],
      "id": "winter-prep-data",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Column - Medals by sport and year {width=65%}\n",
        "\n",
        "### Row - Medals by sport {height=60%}\n"
      ],
      "id": "3db64429"
    },
    {
      "cell_type": "code",
      "metadata": {
        "title": "Medals by sport"
      },
      "source": [
        "#| label: winter-medals-by-sport\n",
        "\n",
        "# Lump the sport column to top 15 categories, grouping others as Other\n",
        "top_15_sports = winter_olympics[\"sport\"].value_counts().nlargest(15).index\n",
        "winter_olympics[\"sport\"] = winter_olympics[\"sport\"].apply(lambda x: x if x in top_15_sports else \"Other\")\n",
        "\n",
        "# Convert the sport column to a categorical type with order based on frequency, and reverse the order\n",
        "winter_olympics[\"sport\"] = pd.Categorical(winter_olympics[\"sport\"], categories = winter_olympics[\"sport\"].value_counts().index[::-1])\n",
        "\n",
        "# Move the Other category of the sport column to the beginning\n",
        "new_order = [\"Other\"] + [cat for cat in winter_olympics[\"sport\"].cat.categories if cat != \"Other\"]\n",
        "winter_olympics[\"sport\"] = winter_olympics[\"sport\"].cat.reorder_categories(new_order)\n",
        "\n",
        "# Plot\n",
        "(\n",
        "    ggplot(winter_olympics, aes(x = \"sport\", fill = \"medal\")) +\n",
        "    geom_bar() +\n",
        "    coord_flip() +\n",
        "    guides(fill = guide_legend(reverse = True)) +\n",
        "    scale_fill_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) +  \n",
        "    labs(\n",
        "        x = \"\",\n",
        "        y = \"\",\n",
        "        fill = \"Medal\"\n",
        "    ) +\n",
        "    theme_minimal() +\n",
        "    theme(\n",
        "        legend_position = \"inside\",\n",
        "        legend_position_inside = (0.9, 0.2),\n",
        "        legend_direction = \"horizontal\",\n",
        "        legend_background = element_rect(fill = \"white\", color = \"gray\"),\n",
        "        figure_size = (8, 3)\n",
        "    )\n",
        ")"
      ],
      "id": "winter-medals-by-sport",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "### Row - Medals by year {height=40%}\n",
        "\n",
        "::: {.card title=\"Medals by year\"}\n",
        "Due to World War II, no olympic games were held in 1940 and 1944.\n"
      ],
      "id": "8a5957e9"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-medals-by-year\n",
        "\n",
        "# Count the occurrences of each medal per year\n",
        "winter_olympics_count = winter_olympics.groupby([\"year\", \"medal\"], observed=True).size().reset_index(name = \"n\")\n",
        "\n",
        "# Plot\n",
        "(\n",
        "    ggplot(winter_olympics_count, aes(x = \"year\", y = \"n\")) +\n",
        "    geom_line(aes(color = \"medal\"), size = 0.5) +\n",
        "    geom_point(aes(fill = \"medal\"), size = 2, color = \"white\") + \n",
        "    guides(color = guide_legend(reverse = True)) + \n",
        "    scale_x_continuous(breaks = range(1896, 2020, 8)) + \n",
        "    scale_color_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) + \n",
        "    scale_fill_manual(\n",
        "        values = {\"Gold\":\"#d4af37\", \"Silver\":\"#c0c0c0\", \"Bronze\":\"#cd7f32\"}\n",
        "    ) + \n",
        "    labs(x = \"Year\", y = \"\", color = \"Medal\", fill = \"Medal\") + \n",
        "    theme_minimal() + \n",
        "    theme(\n",
        "        legend_position = \"inside\",\n",
        "        legend_position_inside = (0.9, 0.2),\n",
        "        legend_direction = \"horizontal\",\n",
        "        legend_background = element_rect(fill = \"white\", color = \"gray\"),\n",
        "        figure_size = (11, 2)\n",
        "    )\n",
        ")"
      ],
      "id": "winter-medals-by-year",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::\n",
        "\n",
        "## Column - Medals by country {width=35%}\n",
        "\n",
        "### Row - Value boxes {height=30%}\n"
      ],
      "id": "cb7b3670"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-calculate-most-medals\n",
        "\n",
        "# Filter for gold medals\n",
        "gold_medals = winter_olympics[winter_olympics['medal'] == 'Gold']\n",
        "# Group by team and count gold medals\n",
        "gold_medal_counts = gold_medals.groupby('team').size()\n",
        "# Find the team with the most gold medals\n",
        "most_gold_medals = gold_medal_counts.idxmax()\n",
        "count_most_gold_medals = gold_medal_counts.max()\n",
        "\n",
        "# Filter for silver medals\n",
        "silver_medals = winter_olympics[winter_olympics['medal'] == 'Silver']\n",
        "# Group by team and count silver medals\n",
        "silver_medal_counts = silver_medals.groupby('team').size()\n",
        "# Find the team with the most silver medals\n",
        "most_silver_medals = silver_medal_counts.idxmax()\n",
        "count_most_silver_medals = silver_medal_counts.max()\n",
        "\n",
        "# Filter for bronze medals\n",
        "bronze_medals = winter_olympics[winter_olympics['medal'] == 'Bronze']\n",
        "# Group by team and count bronze medals\n",
        "bronze_medal_counts = bronze_medals.groupby('team').size()\n",
        "# Find the team with the most bronze medals\n",
        "most_bronze_medals = bronze_medal_counts.idxmax()\n",
        "count_most_bronze_medals = bronze_medal_counts.max()"
      ],
      "id": "winter-calculate-most-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "::: {.valuebox icon=\"award-fill\" color=\"#d4af37\"}\n",
        "Most golds: \n",
        "\n",
        "`{python} str(count_most_gold_medals)`\n",
        "\n",
        "`{python} most_gold_medals`\n",
        ":::\n",
        "\n",
        "::: {.valuebox icon=\"award-fill\" color=\"#c0c0c0\"}\n",
        "Most silvers: \n",
        "\n",
        "`{python} str(count_most_silver_medals)`\n",
        "\n",
        "`{python} most_silver_medals`\n",
        ":::\n",
        "\n",
        "::: {.valuebox icon=\"award-fill\" color=\"#cd7f32\"}\n",
        "Most bronzes: \n",
        "\n",
        "`{python} str(count_most_bronze_medals)`\n",
        "\n",
        "`{python} most_bronze_medals`\n",
        ":::\n",
        "\n",
        "### Row - Tabsets of tables {height=70% .tabset}\n"
      ],
      "id": "b3c336df"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-team-total-medals\n",
        "\n",
        "# Count the occurrences of each medal per team\n",
        "winter_olympics_count = winter_olympics.groupby([\"team\", \"medal\"]).size().reset_index(name=\"n\")\n",
        "\n",
        "# Pivot olympics_count to get medals as columns\n",
        "winter_olympics_pivot = winter_olympics_count.pivot_table(index = \"team\", columns = \"medal\", values = \"n\", fill_value = 0)\n",
        "\n",
        "# Calculate the total number of medals\n",
        "winter_olympics_pivot[\"Total\"] = winter_olympics_pivot[[\"Bronze\", \"Gold\", \"Silver\"]].sum(axis=1)\n",
        "\n",
        "# Reset the index and rearrange columns\n",
        "winter_olympics_pivot = winter_olympics_pivot.reset_index()\n",
        "winter_olympics_pivot = winter_olympics_pivot[[\"team\", \"Gold\", \"Silver\", \"Bronze\", \"Total\"]]\n",
        "\n",
        "# Sort by Total medals, then team\n",
        "winter_olympics_sorted_descending = winter_olympics_pivot.sort_values(by=[\"Total\", \"team\"], ascending=[False, True])\n",
        "winter_olympics_sorted_ascending = winter_olympics_pivot.sort_values(by=[\"Total\", \"team\"], ascending=[True, True])\n",
        "\n",
        "# Remove Total\n",
        "winter_olympics_sorted_descending = winter_olympics_sorted_descending[[\"team\", \"Gold\", \"Silver\", \"Bronze\"]]\n",
        "winter_olympics_sorted_ascending = winter_olympics_sorted_ascending[[\"team\", \"Gold\", \"Silver\", \"Bronze\"]]\n",
        "\n",
        "# Rename the team column to Team\n",
        "winter_olympics_sorted_descending.rename(columns={\"team\": \"Team\"}, inplace=True)\n",
        "winter_olympics_sorted_ascending.rename(columns={\"team\": \"Team\"}, inplace=True)\n",
        "\n",
        "# Find top and bottom 30\n",
        "winter_olympics_sorted_descending_top30 = winter_olympics_sorted_descending.head(30)\n",
        "winter_olympics_sorted_descending_top30.reset_index(drop=True, inplace=True)\n",
        "winter_olympics_sorted_ascending_bottom30 = winter_olympics_sorted_ascending.head(30)\n",
        "winter_olympics_sorted_ascending_bottom30.reset_index(drop=True, inplace=True)"
      ],
      "id": "winter-team-total-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "::: {.card title=\"Top 30 total medals\"}\n",
        "Teams sorted in descending order of total medals.\n"
      ],
      "id": "d7d4fa24"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-top-30-medals\n",
        "(\n",
        "    gt.GT(winter_olympics_sorted_descending_top30).data_color(\n",
        "        columns=[\"Gold\", \"Silver\", \"Bronze\"],\n",
        "        palette=\"Oranges\"\n",
        "    )\n",
        ")"
      ],
      "id": "winter-top-30-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::\n",
        "\n",
        "::: {.card title=\"Bottom 30 total medals\"}\n",
        "Teams sorted in ascending order of total medals.\n"
      ],
      "id": "ebdb3fd8"
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "#| label: winter-bottom-30-medals\n",
        "(\n",
        "    gt.GT(winter_olympics_sorted_ascending_bottom30).data_color(\n",
        "        columns=[\"Gold\", \"Silver\", \"Bronze\"],\n",
        "        palette=\"Blues\"\n",
        "    )\n",
        ")"
      ],
      "id": "winter-bottom-30-medals",
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        ":::"
      ],
      "id": "fb69a7bb"
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
