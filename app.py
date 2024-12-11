import aiohttp
import asyncio
from aiohttp import web
import json
import os

# File to store JSON data
data_file = "products.json"

# Helper function to fetch and save JSON data asynchronously
async def fetch_and_save_json(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Determine if the data represents categories or products
                    if "category" in data[0]:  # Check the first item for a 'category' key
                        data_type = "categories"
                    elif "name" in data[0] and "price" in data[0]:  # Check for product keys
                        data_type = "products"
                    else:
                        return False, "Unknown data format."

                    # Save the data
                    with open(data_file, 'w') as f:
                        json.dump(data, f, indent=4)

                    return True, data_type
                else:
                    return False, f"Failed to fetch data. HTTP Status: {response.status}"
    except Exception as e:
        return False, f"Error fetching data: {e}"

# Handler for the home page
async def home(request):
    return web.Response(text="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <title>Product Management</title>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-8">
            <h1 class="text-2xl font-bold mb-4">Enter URL</h1>
            <form action="/fetch-data" method="post" class="space-y-4">
                <input type="url" name="api_url" placeholder="Enter URL" class="w-full px-4 py-2 border rounded" required />
                <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Fetch Data</button>
            </form>
        </div>
    </body>
    </html>
    """, content_type='text/html')

# Handler to fetch and save JSON data
async def fetch_data(request):
    data = await request.post()
    api_url = data.get('api_url')

    success, result = await fetch_and_save_json(api_url)

    if success:
        # Redirect based on the type of data fetched
        if result == "categories":
            return web.HTTPFound(location='/categories')
        elif result == "products":
            return web.HTTPFound(location='/products')
    else:
        return web.Response(text=f"<p>{result}</p>", content_type='text/html')

# Handler to display categories
async def categories(request):
    if not os.path.exists(data_file):
        return web.Response(text="<p>No data available. Please upload data first.</p>", content_type='text/html')

    with open(data_file, 'r') as f:
        data = json.load(f)

    category_list = ''.join(f'''
        <div class="flex items-center justify-between p-4 border rounded mb-4">
            <span>{item['category']}</span>
            <div>
                <a href="/products?category={item['category']}" class="bg-green-500 text-white px-4 py-2 rounded">View All Products</a>
                <a href="/download-category?category={item['category']}" class="bg-blue-500 text-white px-4 py-2 rounded">Download</a>
            </div>
        </div>
    ''' for item in data)

    return web.Response(text=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <title>Categories</title>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-8">
            <h1 class="text-2xl font-bold mb-4">Categories</h1>
            <div class="flex items-center mb-4">
                <input type="text" placeholder="Search categories..." class="flex-grow px-4 py-2 border rounded" />
                <a href="/download-all" class="bg-blue-500 text-white px-4 py-2 rounded ml-4">Download All</a>
            </div>
            {category_list}
        </div>
    </body>
    </html>
    """, content_type='text/html')

# Handler to display products
async def products(request):
    if not os.path.exists(data_file):
        return web.Response(text="<p>No data available. Please upload data first.</p>", content_type='text/html')

    with open(data_file, 'r') as f:
        data = json.load(f)

    product_list = ''.join(f'''
        <div class="p-4 border rounded mb-4">
            <img src="{item['image']}" alt="{item['name']}" class="w-32 h-32 object-cover mb-2">
            <h2 class="font-bold">{item['name']}</h2>
            <p>${item['price']}</p>
            <p>{item['description']}</p>
            <a href="/download-product?id={item['id']}" class="bg-blue-500 text-white px-4 py-2 rounded">Download</a>
        </div>
    ''' for item in data)

    return web.Response(text=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <title>Products</title>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-8">
            <h1 class="text-2xl font-bold mb-4">Products</h1>
            <div class="flex items-center mb-4">
                <input type="text" placeholder="Search products..." class="flex-grow px-4 py-2 border rounded" />
                <a href="/download-all" class="bg-blue-500 text-white px-4 py-2 rounded ml-4">Download All</a>
            </div>
            {product_list}
        </div>
    </body>
    </html>
    """, content_type='text/html')

# Define the app and routes
app = web.Application()
app.router.add_get('/', home)
app.router.add_post('/fetch-data', fetch_data)
app.router.add_get('/categories', categories)
app.router.add_get('/products', products)

if __name__ == '__main__':
    web.run_app(app, host='localhost', port=8080)
