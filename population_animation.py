import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import os

def setup_plot_style(ax):
    """Set up the plot style for better aesthetics."""
    # Use a clean, professional style
    sns.set_style("whitegrid")
    ax.set_facecolor('#f8f9fa')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Remove unnecessary spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)  # Hide left spine for cleaner look
    ax.spines['bottom'].set_color('#333333')
    
    # Style the ticks
    ax.tick_params(axis='both', colors='#333333', labelsize=10)
    ax.set_yticks([])  # Remove y-ticks for cleaner look
    
    # Add subtle grid only on x-axis
    ax.grid(True, axis='x', linestyle='--', alpha=0.3, color='#666666')

def load_flag_images(countries, flag_folder='./flags', use_iso=False):
    """Load and resize flag images for the countries."""
    flag_images = {}
    
    # Create flags directory if it doesn't exist
    if not os.path.exists(flag_folder):
        os.makedirs(flag_folder)
        print(f"Created directory {flag_folder}. Please add country flag images.")
        return flag_images
    
    # Try multiple extensions in case file format varies
    extensions = ['.png', '.jpg', '.jpeg', '.svg']
    
    for country in countries:
        country_key = country
        
        # Try ISO code file first if available
        if use_iso and 'ISO3_code' in country and country['ISO3_code']:
            iso_code = country['ISO3_code']
            filename = f"{flag_folder}/{iso_code}.png"
            
            if os.path.exists(filename):
                try:
                    img = Image.open(filename)
                    img.thumbnail((50, 30), Image.Resampling.LANCZOS)
                    flag_images[country_key] = img
                    continue  # Skip to next country if found
                except:
                    pass  # Try alternative methods if this fails
        
        # Fall back to country name if ISO code doesn't work
        country_name = country if isinstance(country, str) else country.get('Location', '')
        country_code = country_name.lower().replace(' ', '_')
        
        # Try various filename patterns
        filenames = [f"{flag_folder}/{country_code}{ext}" for ext in extensions]
        
        # Try to load the first file that exists
        for filename in filenames:
            if os.path.exists(filename):
                try:
                    img = Image.open(filename)
                    img.thumbnail((50, 30), Image.Resampling.LANCZOS)
                    flag_images[country_key] = img
                    break
                except:
                    print(f"Could not process flag for {country_name} from {filename}")
        
    return flag_images

def format_population(population):
    """Format population numbers for display."""
    if population >= 1_000_000_000:
        return f"{population/1_000_000_000:.2f}B"
    else:
        return f"{population/1_000_000:.1f}M"

def create_animation(df):
    """Create an animated bar chart showing the top 10 countries by population over time."""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Sort the years for proper animation flow
    frames = sorted(df['Time'].unique())
    
    # Get the unique countries for flag loading
    all_countries = [{'Location': country} for country in df['Location'].unique()]
    flag_images = load_flag_images(all_countries)
    
    # Set up the figure with a specific aspect ratio for presentations
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    
    # Create a color palette for consistent country colors
    countries = pd.Series(df['Location'].unique())
    color_palette = sns.color_palette("viridis", len(countries))
    country_colors = dict(zip(countries, color_palette))
    
    # Create a single clean title
    plt.suptitle('Global Population Trends', 
               fontsize=22, fontweight='bold', y=0.98)
    
    # Add a subtitle
    plt.figtext(0.5, 0.92, 'Top 10 Most Populous Countries by Year', 
              fontsize=16, ha='center', color='#555555')
    
    # Add a watermark/attribution
    plt.figtext(0.95, 0.02, 'Data: UN World Population Prospects', 
              fontsize=8, color='#888888', ha='right')
    
    # Year display - make it large and prominent
    year_display = plt.figtext(0.90, 0.85, '', fontsize=42, 
                             fontweight='bold', color='#333333', alpha=0.8, ha='right')
    
    def animate(frame_idx):
        """Animate function to update the plot for each frame."""
        # Clear previous frame
        ax.clear()
        
        # Get current year
        year = frames[frame_idx]
        year_display.set_text(f"{year}")
        
        # Filter data for current year and get top 10
        pop_data_frame = df[df['Time'] == year]
        top_countries = pop_data_frame.nlargest(10, 'TPopulation1Jan').sort_values('TPopulation1Jan', ascending=True)
        
        # Create bars with consistent colors
        bars = ax.barh(range(len(top_countries)), 
                     top_countries['TPopulation1Jan'],
                     height=0.7,  # Slimmer bars look more elegant
                     alpha=0.7,
                     color=[country_colors[country] for country in top_countries['Location']])
        
        # Add country names and flags on left side
        for i, (_, row) in enumerate(top_countries.iterrows()):
            country = row['Location']
            
            # Add country name
            ax.text(-0.01 * top_countries['TPopulation1Jan'].max(), i, 
                   f"{country} ", 
                   ha='right', va='center',
                   fontsize=12, fontweight='bold')
            
            # Add flag if available
            if country in flag_images:
                img = flag_images[country]
                imagebox = OffsetImage(img, zoom=0.7)
                xy = (-0.04 * top_countries['TPopulation1Jan'].max(), i)
                ab = AnnotationBbox(imagebox, xy, 
                                  frameon=False,
                                  box_alignment=(1, 0.5),
                                  xycoords='data')
                ax.add_artist(ab)
            
            # Add population value at end of bar
            population = row['TPopulation1Jan']
            formatted_pop = format_population(population)
            ax.text(population * 1.01, i, 
                   formatted_pop,
                   va='center', 
                   fontsize=12, 
                   fontweight='bold', 
                   color='#333333')
        
        # Style the plot
        ax.set_xlabel('Population', fontsize=12, labelpad=10)
        
        # Format x-axis with comma separators and millions
        def x_fmt(x, pos):
            if x >= 1_000_000_000:
                return f"{x/1_000_000_000:.1f}B"
            else:
                return f"{x/1_000_000:.0f}M"
        
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(x_fmt))
        
        # Set y-ticks but no labels (we're adding them manually)
        ax.set_yticks(range(len(top_countries)))
        ax.set_yticklabels([])
        
        # Set reasonable x-axis limits with padding
        max_pop = top_countries['TPopulation1Jan'].max()
        ax.set_xlim(-max_pop * 0.3, max_pop * 1.15)  # Negative space for country names
        
        setup_plot_style(ax)
        plt.tight_layout(rect=[0, 0.03, 1, 0.90])  # Adjust layout to accommodate titles
        
    # Create animation with appropriate settings for professional presentation
    anim = animation.FuncAnimation(
        fig,
        animate,
        frames=len(frames),
        interval=600,  # Slower for presentation clarity
        blit=False
    )
    
    return anim, fig

if __name__ == "__main__":
    # Load the data
    df = pd.read_csv('./data/cleaned-data.csv')
    
    # Create the animation
    anim, fig = create_animation(df)
    
    # Save as high-quality MP4 for presentations
    print("Saving animation to MP4...")
    anim.save('population_animation.mp4', 
             writer='ffmpeg', 
             fps=5,
             dpi=200,
             bitrate=5000)
    
    # Save a still of the final frame for thumbnails
    print("Saving final frame as PNG...")
    plt.savefig('population_final_frame.png', dpi=200, bbox_inches='tight')
    
    # Show the animation
    plt.show()


