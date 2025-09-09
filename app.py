import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns


st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    #st.text("Raw chat preview:\n" + "\n".join(data.split("\n")[:20]))

    df = preprocessor.preprocess(data)
    #st.write("Parsed preview:", df.head(20))

    if df.empty:
        st.warning("No valid messages found in this chat file. Please upload a chat exported WITHOUT media.")
    else:
        st.dataframe(df.head())  # Debug preview

        # Fetch users
        user_list = [user for user in df['user'].unique().tolist() if user != 'group_notification']
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

        if st.sidebar.button("Show Analysis"):

            # ---------------- Stats ----------------
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1: st.header("Messages"); st.title(num_messages)
            with col2: st.header("Words"); st.title(words)
            with col3: st.header("Media"); st.title(num_media_messages)
            with col4: st.header("Links"); st.title(num_links)

            # ---------------- Monthly Timeline ----------------
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            if not timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No monthly data available.")

            # ---------------- Daily Timeline ----------------
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            if not daily_timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No daily data available.")

            # ---------------- Activity Map ----------------
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                if not busy_day.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.info("No busy day data.")

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                if not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.info("No busy month data.")

            # ---------------- Heatmap ----------------
            st.title("Weekly Activity Heatmap")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if not user_heatmap.empty:
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, ax=ax)
                st.pyplot(fig)
            else:
                st.info("No heatmap data available.")

            # ---------------- Busy Users ----------------
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                col1, col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # ---------------- Wordcloud ----------------
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)

            # ---------------- Common Words ----------------
            st.title('Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            if not most_common_df.empty:
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No common words found.")

            # ---------------- Emoji Analysis ----------------
            st.title("Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1: st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                    st.pyplot(fig)
            else:
                st.info("No emojis found.")
