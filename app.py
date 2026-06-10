import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Cấu hình trang
st.set_page_config(
    page_title="Phân tích Bão Nhiệt đới Việt Nam",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Màu sắc theo cấp bão (giống notebook 08)
CAT_COLORS = {
    'TD':  '#00cec9',
    'TS':  '#fdcb6e',
    'STS': '#e17055',
    'TY':  '#d63031',
}
CAT_ORDER = ['TD', 'TS', 'STS', 'TY']
CAT_LABEL = {
    'TD':  'TD – Áp thấp nhiệt đới',
    'TS':  'TS – Bão nhiệt đới',
    'STS': 'STS – Bão nhiệt đới mạnh',
    'TY':  'TY – Bão',
}

# Load dữ liệu
@st.cache_data
def load_data():
    df = pd.read_csv('data/final_data/final_dataset.csv')
    df['ISO_TIME'] = pd.to_datetime(df['ISO_TIME'])
    return df

df = load_data()

# Sidebar – Bộ lọc
st.sidebar.title("🌀 Bộ lọc dữ liệu")

year_min, year_max = int(df['YEAR'].min()), int(df['YEAR'].max())
year_range = st.sidebar.slider(
    "Năm", year_min, year_max, (year_min, year_max)
)

basin_options = sorted(df['BASIN'].dropna().unique())
basin_sel = st.sidebar.multiselect(
    "Basin", basin_options, default=basin_options
)

cat_options = ['TD', 'TS', 'STS', 'TY']
cat_sel = st.sidebar.multiselect(
    "Cấp bão (PEAK_CAT_FINAL)", cat_options, default=cat_options
)

season_options = ['Early', 'Peak', 'Late', 'Off']
season_sel = st.sidebar.multiselect(
    "Mùa bão (SEASON)", season_options, default=season_options
)

# Áp bộ lọc
mask = (
    df['YEAR'].between(*year_range) &
    df['BASIN'].isin(basin_sel) &
    df['SEASON'].isin(season_sel)
)
if cat_sel:
    mask &= df['PEAK_CAT_FINAL'].isin(cat_sel) | df['PEAK_CAT_FINAL'].isna()

df_f = df[mask].copy()
storms_f = df_f.drop_duplicates('SID')

st.sidebar.markdown("---")
st.sidebar.metric("Số cơn bão", f"{storms_f.shape[0]:,}")
st.sidebar.metric("Số quan trắc", f"{df_f.shape[0]:,}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tổng quan",
    "🗺️ Quỹ đạo bão",
    "📈 Phân tích cường độ",
    "🔍 Khám phá dữ liệu"
])

# TAB 1 – TỔNG QUAN
with tab1:
    st.title("Phân tích Bão Nhiệt đới Khu vực Việt Nam")
    st.caption("IBTrACS v4 · 2000–2025 · DS108 – UIT")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng cơn bão", f"{storms_f.shape[0]:,}")
    c2.metric("Giai đoạn", f"{year_range[0]}–{year_range[1]}")
    has_int = storms_f[storms_f['HAS_INTENSITY'] == True].shape[0]
    c3.metric("Có dữ liệu cường độ", f"{has_int:,}")
    ty_count = (storms_f['PEAK_CAT_FINAL'] == 'TY').sum()
    c4.metric("Bão cấp TY", f"{ty_count:,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Số cơn bão theo năm")
        yearly = storms_f.groupby('YEAR').size().reset_index(name='count')
        yearly['YEAR'] = yearly['YEAR'].astype(str)
        fig = px.bar(
            yearly, x='YEAR', y='count',
            color_discrete_sequence=['#0984e3'],
            labels={'YEAR': 'Năm', 'count': 'Số cơn bão'}
        )
        fig.update_layout(showlegend=False, margin=dict(b=80, r=30))
        fig.update_xaxes(
            tickmode='array',
            tickvals=yearly['YEAR'].tolist(),
            tickangle=45,
            tickfont=dict(size=9),
            automargin=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Phân bố theo cấp bão")
        peak_dist = storms_f['PEAK_CAT_FINAL'].value_counts().reindex(CAT_ORDER).dropna()
        fig2 = px.bar(
            x=peak_dist.index, y=peak_dist.values,
            color=peak_dist.index,
            color_discrete_map=CAT_COLORS,
            labels={'x': 'Cấp bão', 'y': 'Số cơn bão'}
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Phân bố theo tháng")
        monthly = df_f.drop_duplicates('SID').groupby('MONTH').size().reindex(range(1, 13), fill_value=0).reset_index(
            name='count')
        monthly['MONTH'] = monthly['MONTH'].apply(lambda x: f"T{x}")
        fig3 = px.bar(
            monthly, x='MONTH', y='count',
            category_orders={'MONTH': [f"T{i}" for i in range(1, 13)]},
            color_discrete_sequence=['#6c5ce7'],
            labels={'MONTH': 'Tháng', 'count': 'Số cơn bão'}
        )
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Phân bố theo mùa bão")
        season_dist = storms_f['SEASON'].value_counts().reindex(season_options).dropna()
        fig4 = px.pie(
            values=season_dist.values, names=season_dist.index,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig4, use_container_width=True)

# TAB 2 – QUỸ ĐẠO BÃO (PLOTLY)
with tab2:
    st.subheader("Bản đồ quỹ đạo bão")

    map_type = st.radio(
        "Loại bản đồ", ["Quỹ đạo theo cấp bão", "Heatmap mật độ"],
        horizontal=True
    )

    if map_type == "Quỹ đạo theo cấp bão":
        fig = go.Figure()

        for cat in CAT_ORDER:
            df_cat = df_f[df_f['PEAK_CAT_FINAL'] == cat]
            sids = df_cat['SID'].unique()
            for sid in sids:
                track = df_cat[df_cat['SID'] == sid].sort_values('ISO_TIME')
                fig.add_trace(go.Scattergeo(
                    lat=track['LAT'],
                    lon=track['LON'],
                    mode='lines',
                    line=dict(width=1.2, color=CAT_COLORS[cat]),
                    name=cat,
                    legendgroup=cat,
                    showlegend=(sid == sids[0]),
                    hovertemplate=f"{sid} ({int(track['YEAR'].iloc[0])}) – {cat}<extra></extra>"
                ))
        # Storms không xác định cấp
        df_nan = df_f[df_f['PEAK_CAT_FINAL'].isna()]
        sids_nan = df_nan['SID'].unique()
        for sid in sids_nan:
            track = df_nan[df_nan['SID'] == sid].sort_values('ISO_TIME')
            fig.add_trace(go.Scattergeo(
                lat=track['LAT'],
                lon=track['LON'],
                mode='lines',
                line=dict(width=1, color='#b2bec3'),
                name='Không xác định',
                legendgroup='Không xác định',
                showlegend=(sid == sids_nan[0]),
                hovertemplate=f"{sid} ({int(track['YEAR'].iloc[0])}) – Không xác định<extra></extra>"
            ))
        fig.update_layout(
            geo=dict(
                showland=True, landcolor='#3d3d3d',
                showocean=True, oceancolor='#1a1a2e',
                showcoastlines=True, coastlinecolor='#636e72',
                showcountries=True, countrycolor='#636e72',
                showframe=False,
                projection_type='natural earth',
                center=dict(lat=15, lon=115),
                lataxis=dict(range=[-10, 40]),
                lonaxis=dict(range=[90, 160]),
                bgcolor='black',
            ),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            legend=dict(
                bgcolor='#2d3436', font=dict(color='white'),
                title=dict(text='Cấp bão')
            ),
            height=600,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # Highlight Việt Nam
        fig.add_trace(go.Choropleth(
            locations=['VNM'],
            z=[1],
            colorscale=[[0, 'rgba(9,132,227,0.3)'], [1, 'rgba(9,132,227,0.3)']],
            showscale=False,
            showlegend=False,
            marker_line_color='#0984e3',
            marker_line_width=1.5,
        ))

        st.plotly_chart(fig, use_container_width=True)

    else:
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        from scipy.stats import gaussian_kde
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        df_heat = df_f.dropna(subset=['LAT', 'LON'])

        # Tính KDE trên grid
        lon_grid = np.linspace(90, 160, 300)
        lat_grid = np.linspace(-10, 40, 200)
        LON_G, LAT_G = np.meshgrid(lon_grid, lat_grid)

        xy = np.vstack([df_heat['LON'], df_heat['LAT']])
        kde = gaussian_kde(xy, bw_method=0.08)
        positions = np.vstack([LON_G.ravel(), LAT_G.ravel()])
        density = kde(positions).reshape(LON_G.shape)

        # Vẽ
        fig, ax = plt.subplots(
            figsize=(14, 7),
            subplot_kw={'projection': ccrs.PlateCarree()}
        )
        ax.set_extent([90, 160, -10, 40], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor='#2d3436')
        ax.add_feature(cfeature.OCEAN, facecolor='#1a1a2e')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#636e72')
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#636e72')
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.4)
        gl.xlabel_style = {'color': 'white', 'fontsize': 8}
        gl.ylabel_style = {'color': 'white', 'fontsize': 8}

        # Highlight VN
        import cartopy.io.shapereader as shpreader
        from cartopy.feature import ShapelyFeature

        shpfilename = shpreader.natural_earth(
            resolution='10m', category='cultural', name='admin_0_countries'
        )
        reader = shpreader.Reader(shpfilename)
        vn = [c.geometry for c in reader.records() if c.attributes['ADM0_A3'] == 'VNM']
        if vn:
            vn_feature = ShapelyFeature(vn, ccrs.PlateCarree(),
                                        facecolor='#0984e3', alpha=0.3,
                                        edgecolor='#74b9ff', linewidth=1.5)
            ax.add_feature(vn_feature)

        # Heatmap
        pcm = ax.pcolormesh(
            LON_G, LAT_G, density,
            cmap='YlOrRd', alpha=0.85,
            transform=ccrs.PlateCarree(),
            norm=mcolors.PowerNorm(gamma=0.4, vmin=density.min(), vmax=density.max())
        )
        plt.colorbar(pcm, ax=ax, orientation='vertical',
                     shrink=0.6, pad=0.02, label='Mật độ')

        ax.set_facecolor('#1a1a2e')
        fig.patch.set_facecolor('black')
        ax.set_title('Mật độ phân bố bão 2000–2025',
                     color='white', fontsize=13, pad=10)

        st.pyplot(fig)
        plt.close(fig)

# TAB 3 – PHÂN TÍCH CƯỜNG ĐỘ
with tab3:
    st.subheader("Phân tích cường độ bão")
    st.info("📌 Tab này khóa giai đoạn 2000–2024 để đảm bảo chuỗi thời gian liên tục cho STL. Bộ lọc Basin và Mùa bão từ sidebar vẫn được áp dụng.")

    import numpy as np
    from statsmodels.tsa.seasonal import STL
    from statsmodels.tsa.stattools import acf, pacf
    from scipy.stats import kendalltau

    CAT_COLORS_07 = {'TD': '#639922', 'TS': '#378ADD', 'STS': '#EF9F27', 'TY': '#E24B4A'}
    CAT_LABELS_07 = {
        'TD':  'TD (≤33 kt)',
        'TS':  'TS (34–47 kt)',
        'STS': 'STS (48–63 kt)',
        'TY':  'TY (≥64 kt)',
    }
    SEASON_ORDER = ['Early', 'Peak', 'Late', 'Off']

    # Base data: khóa 2000–2024, kế thừa BASIN + SEASON
    df_obs = df[
        (df['YEAR'] <= 2024) &
        (df['BASIN'].isin(basin_sel)) &
        (df['SEASON'].isin(season_sel))
    ].copy()

    storms_07 = (
        df_obs.drop_duplicates('SID')
        [['SID', 'YEAR', 'PEAK_CAT_FINAL']]
        .dropna(subset=['PEAK_CAT_FINAL'])
        .copy()
    )

    # ── FIG 1 ──────────────────────────────────────────────────────────────
    st.markdown("#### Fig 1 · Phân bố WMO_WIND & WMO_PRES theo cấp")
    st.caption("Violin = hình dạng phân phối · Box bên trong = median & IQR")

    col1, col2 = st.columns(2)
    for col, var, ylabel, title in [
        (col1, 'WMO_WIND', 'Tốc độ gió (knots)', '(a) WMO_WIND theo cấp'),
        (col2, 'WMO_PRES', 'Áp suất (hPa)',       '(b) WMO_PRES theo cấp'),
    ]:
        sub = df_obs[['INTENSITY_CAT_FINAL', var]].dropna()
        fig = go.Figure()
        for cat in CAT_ORDER:
            vals = sub.loc[sub['INTENSITY_CAT_FINAL'] == cat, var]
            fig.add_trace(go.Violin(
                x=[CAT_LABELS_07[cat]] * len(vals),
                y=vals,
                name=CAT_LABELS_07[cat],
                box_visible=True,
                meanline_visible=True,
                fillcolor=CAT_COLORS_07[cat],
                opacity=0.6,
                line_color=CAT_COLORS_07[cat],
                points=False,
            ))
        fig.update_layout(
            title=title,
            yaxis_title=ylabel,
            showlegend=False,
            violingap=0.05,
            violinmode='overlay',
        )
        with col:
            st.plotly_chart(fig, use_container_width=True)

    # ── FIG 2 – STL storms/tháng ───────────────────────────────────────────
    st.markdown("#### Fig 2 · STL Decomposition — Số lượng storms/tháng")
    st.caption("Đơn vị: storms · 1 SID = 1 cơn bão · loại storms không xác định PEAK_CAT_FINAL")

    storm_dates = (
        df_obs.sort_values('ISO_TIME')
        .drop_duplicates('SID', keep='first')
        [['SID', 'ISO_TIME', 'PEAK_CAT_FINAL']]
        .dropna(subset=['PEAK_CAT_FINAL'])
        .copy()
    )
    storm_dates['YM'] = storm_dates['ISO_TIME'].dt.to_period('M')
    monthly_count = (
        storm_dates.groupby('YM').size()
        .rename('n_storms').reset_index()
    )
    monthly_count['date'] = monthly_count['YM'].dt.to_timestamp()
    monthly_count = monthly_count.set_index('date')['n_storms'].sort_index()
    full_idx = pd.date_range('2000-01-01', '2024-12-01', freq='MS')
    monthly_count = monthly_count.reindex(full_idx, fill_value=0)
    monthly_count.index.freq = pd.tseries.frequencies.to_offset('MS')

    stl_count  = STL(monthly_count, period=12, robust=True)
    res_count  = stl_count.fit()
    var_r      = np.var(res_count.resid.values)
    F_T        = max(0, 1 - var_r / (np.var(res_count.trend.values)    + var_r))
    F_S        = max(0, 1 - var_r / (np.var(res_count.seasonal.values) + var_r))
    tau_count, p_mk_count = kendalltau(
        np.arange(len(res_count.trend)), res_count.trend.values
    )

    dates = monthly_count.index
    fig2  = go.Figure()
    for series, color, name, yax in [
        (monthly_count.values,        '#aaaaaa', 'Chuỗi gốc (storms/tháng)', 'y1'),
        (res_count.trend.values,      '#E24B4A', 'Trend (LOESS)',             'y2'),
        (res_count.seasonal.values,   '#378ADD', 'Seasonal (chu kỳ 12 tháng)', 'y3'),
    ]:
        fig2.add_trace(go.Scatter(
            x=dates, y=series,
            mode='lines', name=name,
            line=dict(color=color, width=1.5),
            yaxis=yax,
        ))
    fig2.update_layout(
        height=550,
        title='STL Decomposition — Số lượng storms/tháng (2000–2024)',
        xaxis=dict(domain=[0, 1], anchor='y3'),
        yaxis =dict(domain=[0.68, 1.0],  title='Chuỗi gốc',  title_font_size=10),
        yaxis2=dict(domain=[0.34, 0.64], title='Trend',       title_font_size=10),
        yaxis3=dict(domain=[0.0,  0.30], title='Seasonal',    title_font_size=10),
        legend=dict(orientation='h', y=1.05),
        annotations=[dict(
            x=0.01, y=0.61, xref='paper', yref='paper',
            text=(
                f'Mann-Kendall: tau={tau_count:+.3f}, p={p_mk_count:.4f}<br>'
                f'F_T={F_T:.3f} | {"Trend yếu - không kết luận" if F_T < 0.4 else "Trend đáng kể"}'
            ),
            showarrow=False, align='left',
            bgcolor='#fff0f0', bordercolor='#E24B4A',
            font=dict(size=10),
        )],
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ACF / PACF cho Fig 2
    st.markdown("**ACF & PACF — Chuỗi số lượng storms/tháng**")
    acf_vals  = acf(monthly_count,  nlags=36, fft=True)
    pacf_vals = pacf(monthly_count, nlags=36)
    conf_band = 1.96 / np.sqrt(len(monthly_count))
    lags      = list(range(37))

    col_acf, col_pacf = st.columns(2)
    for col, vals, title_acf in [
        (col_acf,  acf_vals,  'ACF (Autocorrelation Function)'),
        (col_pacf, pacf_vals, 'PACF (Partial Autocorrelation Function)'),
    ]:
        colors_acf = ['#378ADD' if abs(v) > conf_band else '#cccccc' for v in vals]
        fig_acf = go.Figure()
        fig_acf.add_trace(go.Bar(x=lags, y=vals, marker_color=colors_acf))
        fig_acf.add_hline(y= conf_band, line_dash='dash', line_color='#E24B4A', line_width=1.2)
        fig_acf.add_hline(y=-conf_band, line_dash='dash', line_color='#E24B4A', line_width=1.2)
        fig_acf.add_hline(y=0, line_color='#333', line_width=0.8)
        fig_acf.update_layout(
            title=title_acf,
            xaxis_title='Lag (tháng)',
            yaxis_title='Hệ số tương quan',
            showlegend=False,
            height=300,
        )
        with col:
            st.plotly_chart(fig_acf, use_container_width=True)

    # ── FIG 3 – STL Mean WMO_WIND ──────────────────────────────────────────
    st.markdown("#### Fig 3 · STL Decomposition — Mean WMO_WIND/tháng")
    st.caption("Đơn vị: observations · trung bình WMO_WIND tại track point 3 giờ")

    full_idx = pd.date_range('2000-01-01', '2024-12-01', freq='MS')
    monthly_wind = (
        df_obs.dropna(subset=['WMO_WIND'])
        .assign(YM=lambda x: x['ISO_TIME'].dt.to_period('M').dt.to_timestamp())
        .groupby('YM')['WMO_WIND'].mean()
        .reindex(full_idx)
        .interpolate(method='linear')
        .bfill()
        .ffill()
    )
    monthly_wind.index = full_idx
    monthly_wind.index.freq = pd.tseries.frequencies.to_offset('MS')

    stl_wind  = STL(monthly_wind, period=12, robust=True)
    res_wind  = stl_wind.fit()
    var_r_w   = np.var(res_wind.resid.values)
    F_T_w     = max(0, 1 - var_r_w / (np.var(res_wind.trend.values)    + var_r_w))
    F_S_w     = max(0, 1 - var_r_w / (np.var(res_wind.seasonal.values) + var_r_w))
    tau_wind, p_mk_wind = kendalltau(
        np.arange(len(res_wind.trend)), res_wind.trend.values
    )

    dates_w = monthly_wind.index
    fig3    = go.Figure()
    for series, color, name, yax in [
        (monthly_wind.values,          '#378ADD', 'Chuỗi gốc (kt)',             'y1'),
        (res_wind.trend.values,         '#E24B4A', 'Trend',                      'y2'),
        (res_wind.seasonal.values,      '#EF9F27', 'Seasonal (chu kỳ 12 tháng)', 'y3'),
        (res_wind.resid.values,         '#888888', 'Residual',                   'y4'),
    ]:
        fig3.add_trace(go.Scatter(
            x=dates_w, y=series,
            mode='lines', name=name,
            line=dict(color=color, width=1.4),
            yaxis=yax,
        ))
    fig3.update_layout(
        height=650,
        title='STL Decomposition — Mean WMO_WIND/tháng (2000–2024)',
        xaxis=dict(domain=[0, 1], anchor='y4'),
        yaxis =dict(domain=[0.76, 1.0],  title='Chuỗi gốc (kt)', title_font_size=10),
        yaxis2=dict(domain=[0.50, 0.72], title='Trend',           title_font_size=10),
        yaxis3=dict(domain=[0.25, 0.46], title='Seasonal',        title_font_size=10),
        yaxis4=dict(domain=[0.0,  0.21], title='Residual',        title_font_size=10),
        legend=dict(orientation='h', y=1.05),
        annotations=[dict(
            x=0.01, y=0.70, xref='paper', yref='paper',
            text=(
                f'Mann-Kendall: tau={tau_wind:+.3f}, p={p_mk_wind:.4f}<br>'
                f'F_T={F_T_w:.3f} | F_S={F_S_w:.3f}'
            ),
            showarrow=False, align='left',
            bgcolor='#fff0f0', bordercolor='#E24B4A',
            font=dict(size=10),
        )],
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── FIG 4 – Mùa × cấp ─────────────────────────────────────────────────
    st.markdown("#### Fig 4 · Phân bố cấp cường độ theo mùa bão")
    st.caption("Đơn vị: observations (track points 3 giờ)")

    cross = (
        df_obs.dropna(subset=['INTENSITY_CAT_FINAL', 'SEASON'])
        .groupby(['SEASON', 'INTENSITY_CAT_FINAL'])
        .size()
        .unstack(fill_value=0)
        .reindex(index=SEASON_ORDER, columns=CAT_ORDER, fill_value=0)
    )
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100

    col3, col4 = st.columns(2)
    with col3:
        fig4a = go.Figure()
        for cat in CAT_ORDER:
            fig4a.add_trace(go.Bar(
                name=CAT_LABELS_07[cat],
                x=SEASON_ORDER,
                y=cross[cat].values,
                marker_color=CAT_COLORS_07[cat],
                text=cross[cat].values,
                textposition='outside',
                textfont=dict(size=9),
            ))
        fig4a.update_layout(
            barmode='group',
            title='(a) Số observations tuyệt đối',
            yaxis_title='Số observations',
            legend_title_text='Cấp bão',
            bargap=0.15,
        )
        st.plotly_chart(fig4a, use_container_width=True)

    with col4:
        fig4b = go.Figure()
        for cat in CAT_ORDER:
            fig4b.add_trace(go.Bar(
                name=CAT_LABELS_07[cat],
                x=SEASON_ORDER,
                y=cross_pct[cat].round(1).values,
                marker_color=CAT_COLORS_07[cat],
                text=[f'{v:.1f}%' for v in cross_pct[cat].values],
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(size=9, color='white'),
            ))
        fig4b.update_layout(
            barmode='stack',
            title='(b) Tỉ lệ cấp cường độ theo mùa (100%)',
            yaxis=dict(title='Tỉ lệ (%)', ticksuffix='%', range=[0, 110]),
            legend_title_text='Cấp bão',
        )
        for j, season in enumerate(SEASON_ORDER):
            fig4b.add_annotation(
                x=season, y=104,
                text=f"n={cross.loc[season].sum():,}",
                showarrow=False,
                font=dict(size=10, color='#444441'),
            )
        st.plotly_chart(fig4b, use_container_width=True)

# TAB 4 – KHÁM PHÁ DỮ LIỆU
with tab4:
    st.subheader("Khám phá dữ liệu")

    view_mode = st.radio(
        "Xem theo", ["Từng cơn bão", "Toàn bộ quan trắc"], horizontal=True
    )

    if view_mode == "Từng cơn bão":
        display_df = storms_f[[
            'SID', 'YEAR', 'BASIN', 'SEASON',
            'PEAK_CAT_FINAL', 'HAS_INTENSITY'
        ]].reset_index(drop=True)
    else:
        display_df = df_f[[
            'SID', 'ISO_TIME', 'LAT', 'LON',
            'WMO_WIND', 'WMO_PRES',
            'INTENSITY_CAT_FINAL', 'SEASON'
        ]].reset_index(drop=True)

    st.dataframe(display_df, use_container_width=True, height=500)
    st.caption(f"{len(display_df):,} dòng")