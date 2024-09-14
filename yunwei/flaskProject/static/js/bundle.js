import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

function DataTable() {
    const [data, setData] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [perPage, setPerPage] = useState(20);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await fetch('/gethost/data/api');
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const result = await response.json();
                console.log('Fetched data:', result);  // 调试输出
                // 将数据转换为适合表格的格式
                const formattedData = result.map(item => ({
                    Hostname: Object.keys(item)[0],
                    User: item[Object.keys(item)[0]]
                }));
                setData(formattedData);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        fetchData();
    }, []);

    const handleSearch = (event) => {
        setSearchQuery(event.target.value);
    };

    const handlePageChange = (newPage) => {
        setCurrentPage(newPage);
    };

    // 过滤和分页数据
    const filteredData = data.filter(item => 
        item.Hostname.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.User.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    const paginatedData = filteredData.slice((currentPage - 1) * perPage, currentPage * perPage);

    return (
        <div>
            <input type="text" value={searchQuery} onChange={handleSearch} placeholder="Search..." />
            <table>
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>User</th>
                    </tr>
                </thead>
                <tbody>
                    {paginatedData.length > 0 ? (
                        paginatedData.map((item, index) => (
                            <tr key={index}>
                                <td>{item.Hostname}</td>
                                <td>{item.User}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="2">No data available</td>
                        </tr>
                    )}
                </tbody>
            </table>
            <div>
                <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>Previous</button>
                <span>Page {currentPage}</span>
                <button onClick={() => handlePageChange(currentPage + 1)}>Next</button>
            </div>
        </div>
    );
}

ReactDOM.render(<DataTable />, document.getElementById('root'));

